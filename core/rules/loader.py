from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.rules.models import Rule, RuleEffect, RuleMatch
from core.rules.registry import RuleRegistry


class RuleConfigError(ValueError):
    """Raised when a declarative Rule catalog is invalid."""


def load_rules(path: Path) -> RuleRegistry:
    """Load only the versioned data contract; no imports or expressions are evaluated."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuleConfigError(f"unable to read Rule catalog: {path}") from exc
    if raw.get("schema") != "si-agents.rules.v1":
        raise RuleConfigError("unsupported Rule catalog schema")
    entries = raw.get("rules")
    if not isinstance(entries, list) or not entries:
        raise RuleConfigError("Rule catalog must contain a non-empty rules list")
    registry = RuleRegistry()
    for entry in entries:
        if not isinstance(entry, dict):
            raise RuleConfigError("Rule entries must be objects")
        registry.register(_parse_rule(entry))
    return registry


def _parse_rule(entry: dict[str, Any]) -> Rule:
    try:
        events = tuple(entry.get("events", ()))
        payload_equals = entry.get("payload_equals", {})
        if not all(isinstance(item, str) for item in events) or not isinstance(payload_equals, dict):
            raise TypeError
        return Rule(
            id=str(entry["id"]),
            description=str(entry["description"]),
            match=RuleMatch(events=events, payload_equals=payload_equals),
            effect=RuleEffect(str(entry["effect"])),
            priority=int(entry.get("priority", 100)),
            dangerous_only=bool(entry.get("dangerous_only", False)),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise RuleConfigError(f"invalid Rule entry: {entry!r}") from exc
