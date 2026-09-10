from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.teams.models import ContextMode, TaskDefinition, TeamDefinition
from core.teams.registry import TeamRegistry


def load_team_catalog(path: str | Path) -> TeamRegistry:
    """Load and validate the canonical team/workflow catalog using only the stdlib."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("version") != 1:
        raise ValueError("Unsupported or missing team catalog version")

    registry = TeamRegistry()
    for raw in payload.get("teams", []):
        registry.register(_team_from_mapping(raw))

    errors = registry.validate()
    if errors:
        raise ValueError("Invalid team catalog: " + "; ".join(errors))
    return registry


def _team_from_mapping(raw: Any) -> TeamDefinition:
    if not isinstance(raw, dict):
        raise TypeError("Team entries must be objects")
    required = ("id", "name", "description", "members", "tasks")
    missing = [key for key in required if key not in raw]
    if missing:
        raise ValueError(f"Team entry missing required fields: {', '.join(missing)}")

    tasks: list[TaskDefinition] = []
    for task in raw["tasks"]:
        if not isinstance(task, dict):
            raise TypeError("Task entries must be objects")
        task_required = ("id", "agent_id")
        task_missing = [key for key in task_required if key not in task]
        if task_missing:
            raise ValueError(f"Task entry missing required fields: {', '.join(task_missing)}")
        tasks.append(
            TaskDefinition(
                id=task["id"],
                agent_id=task["agent_id"],
                depends_on=tuple(task.get("depends_on", ())),
                context_mode=ContextMode(task.get("context_mode", ContextMode.ISOLATED)),
                max_attempts=int(task.get("max_attempts", 1)),
                requires_evidence=bool(task.get("requires_evidence", False)),
                verification_gate=bool(task.get("verification_gate", False)),
                escalate_to=task.get("escalate_to"),
                metadata=tuple((str(key), str(value)) for key, value in task.get("metadata", {}).items()),
            )
        )

    return TeamDefinition(
        id=raw["id"],
        name=raw["name"],
        description=raw["description"],
        members=tuple(raw["members"]),
        tasks=tuple(tasks),
        max_parallelism=int(raw.get("max_parallelism", 1)),
        required_evidence=bool(raw.get("required_evidence", True)),
    )
