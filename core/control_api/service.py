"""Core Control API service; HTTP transport is deliberately kept separate."""

from __future__ import annotations

import json
from pathlib import Path
from threading import RLock
from types import MappingProxyType
from typing import Any

from core.governance.engine import GovernanceEngine
from core.governance.models import DataClass, GovernanceRequest, RiskLevel
from core.organization.expansion_loader import load_expansion
from core.organization.loader import load_catalog
from core.teams.loader import load_team_catalog

from .models import API_VERSION, ApiEvent, ApiSnapshot, RunRecord, RunStatus, new_id


class ControlApiService:
    """Versioned read model plus governed mutation boundary.

    The service contains no workflow/tool execution. A run POST only creates a
    governed run record; an execution engine remains an explicit downstream concern.
    """

    def __init__(self, root: str | Path, governance: GovernanceEngine | None = None) -> None:
        self.root = Path(root).resolve()
        self.governance = governance or GovernanceEngine()
        self._lock = RLock()
        self._runs: dict[str, RunRecord] = {}
        self._events: list[ApiEvent] = []
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
            return ApiSnapshot(API_VERSION, "SI-Agents Control API", MappingProxyType({
                "agents": len(self._agents.all()), "teams": len(self._teams.all()),
                "workflows": len(self._organization.workflows), "runs": len(self._runs),
                "events": len(self._events),
            }))

    def agents(self) -> list[dict[str, object]]:
        return [{"id": a.id, "name": a.name, "division": a.division, "status": a.status.value}
                for a in sorted(self._agents.all(), key=lambda item: (item.division, item.name, item.id))]

    def teams(self) -> list[dict[str, object]]:
        return [{"id": t.id, "name": t.name, "description": t.description, "tasks": [x.id for x in t.tasks]}
                for t in sorted(self._teams.all(), key=lambda item: item.id)]

    def organization(self) -> dict[str, object]:
        return {
            "teams": [{"id": t.id, "name": t.name, "purpose": t.purpose,
                       "division_ids": list(t.division_ids), "member_agent_ids": list(t.member_agent_ids),
                       "lead_agent_id": t.lead_agent_id} for t in self._organization.teams],
            "division_assignments": [{"division_id": a.division_id, "team_id": a.team_id,
                                      "rationale": a.rationale} for a in self._organization.division_assignments],
            "workflows": [{"id": w.id, "name": w.name, "purpose": w.purpose, "steps": [
                {"id": s.id, "kind": s.kind.value, "team_id": s.team_id, "agent_id": s.agent_id,
                 "purpose": s.purpose, "depends_on": list(s.depends_on)} for s in w.steps]} for w in self._organization.workflows],
        }

    def workflows(self) -> list[dict[str, object]]:
        return list(self.organization()["workflows"])

    def skills(self) -> list[dict[str, object]]:
        skills_root = self.root / "skills"
        if not skills_root.exists():
            return []
        return [{"id": path.parent.name, "path": str(path.relative_to(self.root))}
                for path in sorted(skills_root.rglob("SKILL.md"))]

    def memory(self) -> dict[str, object]:
        return {"entries": [], "note": "Memory read model is intentionally not an authority; core.memory owns persistence."}

    def governance_state(self) -> dict[str, object]:
        snapshot = self.governance.store.snapshot()
        return {
            "permissions": [{"subject": x.subject, "capability": x.capability, "scope": x.scope,
                             "effect": x.effect.value, "conditions": list(x.conditions)} for x in snapshot.permissions],
            "policies": [{"name": x.name, "description": x.description, "deny_capabilities": list(x.deny_capabilities),
                          "approval_risks": [r.value for r in x.approval_risks], "max_cost": x.max_cost,
                          "allow_external_egress": x.allow_external_egress} for x in snapshot.policies],
            "capabilities": [{"name": x.name, "description": x.description, "risk": x.risk.value}
                              for x in snapshot.capabilities],
        }

    def events(self) -> list[dict[str, object]]:
        with self._lock:
            return [event.as_dict() for event in self._events]

    def runs(self) -> list[dict[str, object]]:
        with self._lock:
            return [run.as_dict() for run in self._runs.values()]

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
            action=action, risk=risk, data_class=data_class, external_egress=bool(payload.get("external_egress", False)),
            paid_resource=bool(payload.get("paid_resource", False)), destructive=bool(payload.get("destructive", False)),
            production=bool(payload.get("production", False)), credential=bool(payload.get("credential", False)),
            publication=bool(payload.get("publication", False)), estimated_cost=estimated_cost,
            capabilities=tuple(capabilities), subject=subject, provenance=tuple(provenance),
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
