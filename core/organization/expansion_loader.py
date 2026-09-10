from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.organization.expansion import (
    DivisionAssignment,
    OrganizationExpansion,
    TeamDefinition,
    WorkflowDefinition,
    WorkflowStep,
    WorkflowStepKind,
)
from core.organization.loader import load_catalog


def load_expansion(path: str | Path, agent_catalog_path: str | Path) -> OrganizationExpansion:
    """Load the declarative organization layer and validate it against the agent source of truth."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("version") != 1:
        raise ValueError("Unsupported or missing organization expansion version")

    catalog = load_catalog(agent_catalog_path)
    expansion = OrganizationExpansion(
        version=1,
        teams=tuple(_team(item) for item in _list(payload, "teams")),
        division_assignments=tuple(_assignment(item) for item in _list(payload, "division_assignments")),
        workflows=tuple(_workflow(item) for item in _list(payload, "workflows")),
    )
    errors = expansion.validate(catalog.all_divisions(), catalog.all())
    if errors:
        raise ValueError("Invalid organization expansion: " + "; ".join(errors))
    return expansion


def _list(payload: dict[str, Any], key: str) -> list[Any]:
    value = payload.get(key, [])
    if not isinstance(value, list):
        raise TypeError(f"Organization field {key} must be a list")
    return value


def _required(raw: Any, *keys: str) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise TypeError("Organization entries must be objects")
    missing = [key for key in keys if key not in raw]
    if missing:
        raise ValueError("Organization entry missing required fields: " + ", ".join(missing))
    return {key: raw[key] for key in keys}


def _strings(raw: Any, key: str) -> tuple[str, ...]:
    value = raw.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise TypeError(f"Organization field {key} must be a list of strings")
    return tuple(value)


def _team(raw: Any) -> TeamDefinition:
    values = _required(raw, "id", "name", "purpose", "division_ids", "member_agent_ids", "lead_agent_id")
    return TeamDefinition(
        id=values["id"],
        name=values["name"],
        purpose=values["purpose"],
        division_ids=_strings(raw, "division_ids"),
        member_agent_ids=_strings(raw, "member_agent_ids"),
        lead_agent_id=values["lead_agent_id"],
    )


def _assignment(raw: Any) -> DivisionAssignment:
    values = _required(raw, "division_id", "team_id", "rationale")
    return DivisionAssignment(**values)


def _workflow(raw: Any) -> WorkflowDefinition:
    values = _required(raw, "id", "name", "purpose", "steps")
    steps = values["steps"]
    if not isinstance(steps, list):
        raise TypeError("Workflow steps must be a list")
    return WorkflowDefinition(
        id=values["id"],
        name=values["name"],
        purpose=values["purpose"],
        steps=tuple(_step(step) for step in steps),
    )


def _step(raw: Any) -> WorkflowStep:
    values = _required(raw, "id", "kind", "team_id", "agent_id", "purpose")
    return WorkflowStep(
        id=values["id"],
        kind=WorkflowStepKind(values["kind"]),
        team_id=values["team_id"],
        agent_id=values["agent_id"],
        purpose=values["purpose"],
        depends_on=_strings(raw, "depends_on"),
    )
