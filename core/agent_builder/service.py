from __future__ import annotations

import json
import os
from dataclasses import replace
from pathlib import Path
from threading import RLock
from typing import Any

from core.organization.loader import load_catalog
from core.organization.models import AgentDefinition

from .models import AgentDraft, DraftStatus, ValidationResult, validate_shape


class AgentBuilderService:
    """Build and validate user-authored agent drafts without changing canonical agents."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()
        catalog_path = self.root / "config" / "agent-catalog.json"
        if not catalog_path.exists():
            catalog_path = Path(__file__).resolve().parents[2] / "config" / "agent-catalog.json"
        self.catalog = load_catalog(catalog_path)
        self._lock = RLock()
        self._path = self.root / ".si" / "agent-builder.json"
        self._drafts: dict[str, AgentDraft] = self._load()

    def _load(self) -> dict[str, AgentDraft]:
        if not self._path.exists():
            return {}
        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("invalid agent builder store") from exc
        if not isinstance(raw, dict) or raw.get("version") != 1 or not isinstance(raw.get("drafts"), list):
            raise ValueError("unsupported agent builder store")
        result: dict[str, AgentDraft] = {}
        for item in raw["drafts"]:
            result[item["id"]] = AgentDraft(
                id=item["id"], name=item["name"], division=item["division"], description=item["description"],
                responsibilities=tuple(item["responsibilities"]), deliverables=tuple(item["deliverables"]),
                success_criteria=tuple(item["success_criteria"]), boundaries=tuple(item["boundaries"]),
                skills=tuple(item.get("skills", ())), capabilities=tuple(item.get("capabilities", ())),
                permissions=tuple(item.get("permissions", ())), harnesses=tuple(item.get("harnesses", ())),
                environments=tuple(item.get("environments", ())), base_agent_id=item.get("base_agent_id"),
                status=DraftStatus(item.get("status", DraftStatus.DRAFT)), revision=int(item.get("revision", 1)),
            )
        return result

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = {"version": 1, "drafts": [self._as_dict(x) for x in sorted(self._drafts.values(), key=lambda d: d.id)]}
        tmp = self._path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        os.replace(tmp, self._path)
        try:
            self._path.chmod(0o600)
        except OSError:
            pass

    @staticmethod
    def _as_dict(draft: AgentDraft) -> dict[str, object]:
        return {
            "id": draft.id, "name": draft.name, "division": draft.division, "description": draft.description,
            "responsibilities": list(draft.responsibilities), "deliverables": list(draft.deliverables),
            "success_criteria": list(draft.success_criteria), "boundaries": list(draft.boundaries),
            "skills": list(draft.skills), "capabilities": list(draft.capabilities), "permissions": list(draft.permissions),
            "harnesses": list(draft.harnesses), "environments": list(draft.environments),
            "base_agent_id": draft.base_agent_id, "status": draft.status.value, "revision": draft.revision,
        }

    def list(self) -> list[dict[str, object]]:
        with self._lock:
            return [self._as_dict(x) for x in sorted(self._drafts.values(), key=lambda d: d.id)]

    def get(self, draft_id: str) -> dict[str, object]:
        with self._lock:
            draft = self._drafts.get(draft_id)
            if draft is None:
                raise KeyError(draft_id)
            return self._as_dict(draft)

    def from_agent(self, agent_id: str) -> dict[str, object]:
        agent = self.catalog.get(agent_id)
        draft = AgentDraft(
            id=agent.id, name=agent.name, division=agent.division, description=agent.description,
            responsibilities=agent.responsibilities, deliverables=agent.deliverables,
            success_criteria=agent.success_criteria, boundaries=agent.boundaries, skills=agent.skills,
            capabilities=agent.capabilities, permissions=agent.permissions, harnesses=agent.harnesses,
            environments=agent.environments, base_agent_id=agent.id,
        )
        return self._as_dict(draft)

    def validate_payload(self, payload: dict[str, Any]) -> ValidationResult:
        draft = self._parse(payload)
        return self._validate(draft)

    def save(self, payload: dict[str, Any]) -> dict[str, object]:
        draft = self._parse(payload)
        result = self._validate(draft)
        if not result.valid:
            raise ValueError("agent draft is invalid: " + "; ".join(result.errors))
        with self._lock:
            previous = self._drafts.get(draft.id)
            if previous is not None and draft.revision <= previous.revision:
                draft = replace(draft, revision=previous.revision + 1)
            self._drafts[draft.id] = replace(draft, status=DraftStatus.VALID)
            self._save()
            return self._as_dict(self._drafts[draft.id])

    def archive(self, draft_id: str) -> dict[str, object]:
        with self._lock:
            draft = self._drafts.get(draft_id)
            if draft is None:
                raise KeyError(draft_id)
            self._drafts[draft_id] = replace(draft, status=DraftStatus.ARCHIVED, revision=draft.revision + 1)
            self._save()
            return self._as_dict(self._drafts[draft_id])

    def test(self, draft_id: str) -> ValidationResult:
        with self._lock:
            draft = self._drafts.get(draft_id)
            if draft is None:
                raise KeyError(draft_id)
        return self._validate(draft)

    def _validate(self, draft: AgentDraft) -> ValidationResult:
        errors = list(validate_shape(draft))
        warnings: list[str] = []
        division_ids = {x.id for x in self.catalog.all_divisions()}
        if draft.division not in division_ids:
            errors.append(f"unknown division: {draft.division}")
        base: AgentDefinition | None = None
        if draft.base_agent_id:
            try:
                base = self.catalog.get(draft.base_agent_id)
            except KeyError:
                errors.append(f"unknown base agent: {draft.base_agent_id}")
            else:
                if draft.id != base.id:
                    errors.append("customization of an existing agent must retain its canonical id")
                if draft.division != base.division:
                    errors.append("customization cannot change an existing agent's division")
                for field in ("permissions", "capabilities", "harnesses", "environments"):
                    before = set(getattr(base, field))
                    after = set(getattr(draft, field))
                    added = sorted(after - before)
                    if added:
                        errors.append(f"customization cannot add {field}: {', '.join(added)}")
        else:
            if draft.id in {x.id for x in self.catalog.all()}:
                errors.append("new draft id collides with a canonical agent")
            if draft.capabilities or draft.permissions or draft.harnesses or draft.environments:
                errors.append("new agents cannot self-grant capabilities, permissions, harnesses, or environments")
            warnings.append("new agents remain drafts and are not added to the canonical catalog")
        if draft.status is DraftStatus.PUBLISHED:
            warnings.append("published status is informational; canonical catalog membership still requires an explicit release process")
        if errors:
            return ValidationResult(False, tuple(errors), tuple(warnings))
        agent = self._agent_projection(draft)
        return ValidationResult(True, (), tuple(warnings), agent, self.render_markdown(draft))

    @staticmethod
    def _agent_projection(draft: AgentDraft) -> dict[str, object]:
        return {
            "id": draft.id, "name": draft.name, "division": draft.division, "description": draft.description,
            "responsibilities": list(draft.responsibilities), "deliverables": list(draft.deliverables),
            "success_criteria": list(draft.success_criteria), "boundaries": list(draft.boundaries),
            "skills": list(draft.skills), "capabilities": list(draft.capabilities), "permissions": list(draft.permissions),
            "harnesses": list(draft.harnesses), "environments": list(draft.environments),
        }

    @staticmethod
    def render_markdown(draft: AgentDraft) -> str:
        def section(title: str, values: tuple[str, ...]) -> str:
            return "\n".join([f"## {title}", *[f"- {x}" for x in values]])
        return "\n\n".join([
            f"# {draft.name}", f"**ID:** `{draft.id}`\n**Division:** `{draft.division}`",
            draft.description, section("Responsibilities", draft.responsibilities),
            section("Deliverables", draft.deliverables), section("Success Criteria", draft.success_criteria),
            section("Boundaries", draft.boundaries), section("Skills", draft.skills or ("None declared",)),
            section("Capabilities", draft.capabilities or ("None declared",)),
            section("Permissions", draft.permissions or ("None declared",)),
            section("Harnesses", draft.harnesses or ("None declared",)),
            section("Environments", draft.environments or ("None declared",)),
            "_Builder output is an authoring artifact. It does not execute code or grant authority._",
        ]) + "\n"

    @staticmethod
    def _parse(payload: dict[str, Any]) -> AgentDraft:
        if not isinstance(payload, dict):
            raise TypeError("agent draft must be a JSON object")
        def strings(key: str) -> tuple[str, ...]:
            value = payload.get(key, [])
            if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
                raise ValueError(f"{key} must be a list of strings")
            return tuple(value)
        return AgentDraft(
            id=str(payload.get("id", "")), name=str(payload.get("name", "")),
            division=str(payload.get("division", "")), description=str(payload.get("description", "")),
            responsibilities=strings("responsibilities"), deliverables=strings("deliverables"),
            success_criteria=strings("success_criteria"), boundaries=strings("boundaries"),
            skills=strings("skills"), capabilities=strings("capabilities"), permissions=strings("permissions"),
            harnesses=strings("harnesses"), environments=strings("environments"),
            base_agent_id=payload.get("base_agent_id") if isinstance(payload.get("base_agent_id"), str) else None,
            status=DraftStatus(payload.get("status", DraftStatus.DRAFT)), revision=int(payload.get("revision", 1)),
        )
