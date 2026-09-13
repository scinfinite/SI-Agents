"""Core Control API service; HTTP transport is deliberately kept separate."""
from __future__ import annotations

import json
import os
import platform
from pathlib import Path
from threading import RLock
from typing import Any

from core.governance.engine import GovernanceEngine
from core.governance.models import DataClass, GovernanceRequest, RiskLevel
from core.hitl import ApprovalState, HumanApprovalService
from core.organization.expansion_loader import load_expansion
from core.organization.loader import load_catalog
from core.teams.loader import load_team_catalog

from .models import API_VERSION, ApiEvent, ApiSnapshot, RunRecord, RunStatus, new_id


class ControlApiService:
    """Versioned read model plus governed mutation boundary."""

    def __init__(self, root: str | Path, governance: GovernanceEngine | None = None) -> None:
        self.root = Path(root).resolve()
        self.governance = governance or GovernanceEngine()
        self._lock = RLock()
        self._runs: dict[str, RunRecord] = {}
        self._events: list[ApiEvent] = []
        self.approvals = HumanApprovalService(self.root / ".si" / "approvals.v1.sqlite3")
        catalog_path = self._path("agent-catalog.json")
        self._agents = load_catalog(catalog_path)
        self._teams = load_team_catalog(self._path("team-catalog.json"))
        self._organization = load_expansion(self._path("organization-expansion.v1.json"), catalog_path)

    def _path(self, filename: str) -> Path:
        source = self.root / "config" / filename
        if source.exists():
            return source
        installed = Path(__file__).resolve().parents[2] / "config" / filename
        if installed.exists():
            return installed
        raise FileNotFoundError(f"canonical catalog not found: {filename}")

    def snapshot(self) -> ApiSnapshot:
        with self._lock:
            counts = (
                ("agents", len(self._agents.all())),
                ("teams", len(self._teams.all())),
                ("workflows", len(self._organization.workflows)),
                ("runs", len(self._runs)),
                ("events", len(self._events)),
            )
            return ApiSnapshot(API_VERSION, "SI-Agents Control API", counts)

    def agents(self) -> list[dict[str, object]]:
        return [
            {"id": a.id, "name": a.name, "division": a.division, "status": a.status.value}
            for a in sorted(self._agents.all(), key=lambda item: (item.division, item.name, item.id))
        ]

    def teams(self) -> list[dict[str, object]]:
        return [
            {"id": t.id, "name": t.name, "description": t.description, "tasks": [x.id for x in t.tasks]}
            for t in sorted(self._teams.all(), key=lambda item: item.id)
        ]

    def organization(self) -> dict[str, object]:
        return {
            "teams": [
                {"id": t.id, "name": t.name, "purpose": t.purpose, "division_ids": list(t.division_ids), "member_agent_ids": list(t.member_agent_ids), "lead_agent_id": t.lead_agent_id}
                for t in self._organization.teams
            ],
            "division_assignments": [
                {"division_id": a.division_id, "team_id": a.team_id, "rationale": a.rationale}
                for a in self._organization.division_assignments
            ],
            "workflows": [
                {
                    "id": w.id,
                    "name": w.name,
                    "purpose": w.purpose,
                    "steps": [
                        {"id": s.id, "kind": s.kind.value, "team_id": s.team_id, "agent_id": s.agent_id, "purpose": s.purpose, "depends_on": list(s.depends_on)}
                        for s in w.steps
                    ],
                }
                for w in self._organization.workflows
            ],
        }

    def workflows(self) -> list[dict[str, object]]:
        return list(self.organization()["workflows"])

    def skills(self) -> list[dict[str, object]]:
        skills_root = self.root / "skills"
        if not skills_root.exists():
            return []
        return [
            {"id": path.parent.name, "path": str(path.relative_to(self.root))}
            for path in sorted(skills_root.rglob("SKILL.md"))
        ]

    def memory(self) -> dict[str, object]:
        return {"entries": [], "note": "Memory read model is intentionally not an authority; core.memory owns persistence."}

    def governance_state(self) -> dict[str, object]:
        snapshot = self.governance.store.snapshot()
        return {
            "permissions": [
                {"subject": x.subject, "capability": x.capability, "scope": x.scope, "effect": x.effect.value, "conditions": list(x.conditions)}
                for x in snapshot.permissions
            ],
            "policies": [
                {"name": x.name, "description": x.description, "deny_capabilities": list(x.deny_capabilities), "approval_risks": [r.value for r in x.approval_risks], "max_cost": x.max_cost, "allow_external_egress": x.allow_external_egress}
                for x in snapshot.policies
            ],
            "capabilities": [{"name": x.name, "description": x.description, "risk": x.risk.value} for x in snapshot.capabilities],
        }

    def evidence(self) -> dict[str, object]:
        with self._lock:
            return {
                "events": [event.as_dict() for event in self._events],
                "run_count": len(self._runs),
                "queued_runs": sum(run.status is RunStatus.QUEUED for run in self._runs.values()),
                "note": "Execution evidence is produced by downstream execution and verification components; this view reports only control-plane evidence.",
            }

    def environments(self) -> dict[str, object]:
        termux = bool(os.environ.get("TERMUX_VERSION")) or "/com.termux/" in os.environ.get("PREFIX", "")
        codespace = bool(os.environ.get("CODESPACES"))
        kind = "termux" if termux else "codespace" if codespace else "unknown"
        return {"current": {"kind": kind, "platform": platform.system().lower(), "architecture": platform.machine(), "python_version": platform.python_version(), "cwd": str(self.root)}, "supported": ["termux", "codespace", "unknown"], "mutations": "read-only"}

    def harnesses(self) -> list[dict[str, object]]:
        adapters = self.root / "adapters"
        if not adapters.exists():
            return []
        return [{"id": path.name, "path": str(path.relative_to(self.root)), "state": "registered"} for path in sorted(adapters.iterdir()) if path.is_dir() and not path.name.startswith(".")]

    def settings(self) -> dict[str, object]:
        return {"api_version": API_VERSION, "web": {"default_host": "127.0.0.1", "default_port": 8788, "remote": "explicit opt-in with authentication"}, "security": {"cors": "explicit allowlist only", "telemetry": "disabled", "mutation_body_limit": "1 MiB"}, "execution": {"run_creation": "governed and queued only", "execution": "downstream"}, "human_in_the_loop": {"approval_decisions": "identity-bound and audited", "expiry": "fail-closed", "execution_authority": "downstream re-authorization required"}}

    def visualization(self) -> dict[str, object]:
        agents = sorted(self._agents.all(), key=lambda item: item.id)
        teams = sorted(self._organization.teams, key=lambda item: item.id)
        assignments = {item.division_id: item.team_id for item in self._organization.division_assignments}
        nodes: dict[str, dict[str, object]] = {}
        edges: set[tuple[str, str, str]] = set()

        def add_node(node_id: str, kind: str, label: str, **extra: object) -> None:
            nodes[node_id] = {"id": node_id, "kind": kind, "label": label, **extra}

        def add_edge(source: str, target: str, relation: str) -> None:
            if source != target:
                edges.add((source, target, relation))

        for team in teams:
            add_node(f"team:{team.id}", "team", team.name, description=team.purpose)
        for agent in agents:
            division_id = agent.division
            add_node(f"division:{division_id}", "division", division_id)
            add_node(f"agent:{agent.id}", "agent", agent.name, status=agent.status.value, division=division_id, skills=list(agent.skills), capabilities=list(agent.capabilities), permissions=list(agent.permissions))
            team_id = assignments.get(division_id)
            if team_id:
                add_edge(f"team:{team_id}", f"division:{division_id}", "owns")
            add_edge(f"division:{division_id}", f"agent:{agent.id}", "contains")
            for skill in agent.skills:
                skill_id = f"skill:{skill}"
                add_node(skill_id, "skill", skill)
                add_edge(f"agent:{agent.id}", skill_id, "uses")
            for capability in agent.capabilities:
                cap_id = f"capability:{capability}"
                add_node(cap_id, "capability", capability)
                add_edge(f"agent:{agent.id}", cap_id, "requests")
            for permission in agent.permissions:
                perm_id = f"permission:{agent.id}:{permission}"
                add_node(perm_id, "permission", permission, subject=agent.id)
                add_edge(f"agent:{agent.id}", perm_id, "declares")
        for permission in self.governance.store.snapshot().permissions:
            cap_id = f"capability:{permission.capability}"
            add_node(cap_id, "capability", permission.capability)
            subject_id = f"agent:{permission.subject}"
            if subject_id in nodes:
                add_edge(subject_id, cap_id, f"governance:{permission.effect.value}")
        for workflow in self._organization.workflows:
            workflow_id = f"workflow:{workflow.id}"
            add_node(workflow_id, "workflow", workflow.name, purpose=workflow.purpose)
            for step in workflow.steps:
                step_id = f"step:{workflow.id}:{step.id}"
                add_node(step_id, "step", step.id, workflow=workflow.id, step_kind=step.kind.value, purpose=step.purpose)
                add_edge(workflow_id, step_id, "contains")
                target = f"agent:{step.agent_id}" if step.agent_id else f"team:{step.team_id}"
                if target in nodes:
                    add_edge(step_id, target, "assigned")
                for dependency in step.depends_on:
                    add_edge(f"step:{workflow.id}:{dependency}", step_id, "depends_on")
        with self._lock:
            runs = [run.as_dict() for run in self._runs.values()]
        return {"version": "v1", "nodes": [nodes[key] for key in sorted(nodes)], "edges": [{"source": source, "target": target, "relation": relation} for source, target, relation in sorted(edges)], "runs": runs, "state_note": "Run state is control-plane state; execution progress is downstream and is not inferred here."}

    def events(self) -> list[dict[str, object]]:
        with self._lock:
            return [event.as_dict() for event in self._events]

    def runs(self) -> list[dict[str, object]]:
        with self._lock:
            return [run.as_dict() for run in self._runs.values()]

    def approvals_queue(self, *, subject_id: str, project_id: str, limit: int = 100) -> list[dict[str, object]]:
        return [item.as_dict() for item in self.approvals.queue(subject_id=subject_id, project_id=project_id, limit=limit)]

    def get_approval(self, approval_id: str, *, subject_id: str, project_id: str) -> dict[str, object]:
        return self.approvals.get(approval_id, subject_id=subject_id, project_id=project_id).as_dict()

    def create_approval(self, payload: dict[str, object]) -> dict[str, object]:
        request = self.approvals.create(payload)
        with self._lock:
            self._events.append(ApiEvent(new_id("evt"), "approval.requested", request.subject_id, metadata={"approval_id": request.approval_id, "gate": request.gate}))
        return request.as_dict()

    def decide_approval(self, approval_id: str, payload: dict[str, object]) -> dict[str, object]:
        subject_id = payload.get("subject_id")
        project_id = payload.get("project_id")
        if not isinstance(subject_id, str) or not isinstance(project_id, str):
            raise ValueError("subject_id and project_id are required")
        decision = payload.get("decision")
        if not isinstance(decision, str):
            raise ValueError("decision is required")
        try:
            state = ApprovalState(decision)
        except ValueError as exc:
            raise ValueError("unsupported decision") from exc
        result_payload = payload.get("result", {})
        if not isinstance(result_payload, dict):
            result_payload = {}
        expected_revision = payload.get("expected_revision")
        if not isinstance(expected_revision, int):
            expected_revision = None
        result = self.approvals.decide(approval_id, subject_id=subject_id, project_id=project_id, decision=state, decision_by=str(payload.get("decision_by", "")), reason=str(payload.get("reason", "")), payload=result_payload, expected_revision=expected_revision)
        with self._lock:
            self._events.append(ApiEvent(new_id("evt"), "approval.decided", subject_id, metadata={"approval_id": approval_id, "state": result.state.value, "decision_by": result.decision_by}))
        return result.as_dict()

    def approval_events(self, approval_id: str, *, subject_id: str, project_id: str) -> list[dict[str, object]]:
        return self.approvals.events(approval_id, subject_id=subject_id, project_id=project_id)

    def get_run(self, run_id: str) -> dict[str, object]:
        with self._lock:
            run = self._runs.get(run_id)
            if run is None:
                raise KeyError(run_id)
            return run.as_dict()

    def create_run(self, payload: dict[str, Any]) -> dict[str, object]:
        action = payload.get("action")
        subject = payload.get("subject")
        if not isinstance(action, str) or not action.strip():
            raise ValueError("action is required")
        if not isinstance(subject, str) or not subject.strip():
            raise ValueError("subject is required")
        capabilities = payload.get("capabilities", [])
        provenance = payload.get("provenance", [])
        if not isinstance(capabilities, list) or not all(isinstance(x, str) for x in capabilities):
            raise ValueError("capabilities must be a list of strings")
        if not isinstance(provenance, list) or not all(isinstance(x, str) for x in provenance):
            raise ValueError("provenance must be a list of strings")
        try:
            risk = RiskLevel(payload.get("risk", RiskLevel.LOW.value))
            data_class = DataClass(payload.get("data_class", DataClass.PUBLIC.value))
            estimated_cost = float(payload.get("estimated_cost", 0.0))
        except (ValueError, TypeError) as exc:
            raise ValueError("invalid risk, data_class, or estimated_cost") from exc
        if estimated_cost < 0:
            raise ValueError("estimated_cost must be non-negative")
        request = GovernanceRequest(
            action=action,
            risk=risk,
            data_class=data_class,
            external_egress=bool(payload.get("external_egress", False)),
            paid_resource=bool(payload.get("paid_resource", False)),
            destructive=bool(payload.get("destructive", False)),
            production=bool(payload.get("production", False)),
            credential=bool(payload.get("credential", False)),
            publication=bool(payload.get("publication", False)),
            estimated_cost=estimated_cost,
            capabilities=tuple(capabilities),
            subject=subject,
            provenance=tuple(provenance),
        )
        decision = self.governance.decide(request)
        if decision.status.value != "allow":
            raise PermissionError(json.dumps({"status": decision.status.value, "reasons": list(decision.reasons)}))
        run = RunRecord(new_id("run"), action, RunStatus.QUEUED, subject, governance_status=decision.status.value)
        event = ApiEvent(new_id("evt"), "run.accepted", subject, metadata={"run_id": run.id, "action": action})
        with self._lock:
            self._runs[run.id] = run
            self._events.append(event)
        return run.as_dict()
