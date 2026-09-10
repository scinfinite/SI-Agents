from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from types import MappingProxyType
from typing import Any
from uuid import uuid4


class EventName(str, Enum):
    SESSION_CREATED = "session.created"
    SESSION_CLOSED = "session.closed"
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    AGENT_SELECTED = "agent.selected"
    SKILL_STARTED = "skill.started"
    SKILL_COMPLETED = "skill.completed"
    TOOL_BEFORE = "tool.before"
    TOOL_AFTER = "tool.after"
    HANDOFF_CREATED = "handoff.created"
    VERIFICATION_STARTED = "verification.started"
    VERIFICATION_FAILED = "verification.failed"
    MEMORY_CREATED = "memory.created"
    MEMORY_PROMOTED = "memory.promoted"
    MEMORY_EXPIRED = "memory.expired"
    MEMORY_REJECTED = "memory.rejected"
    KNOWLEDGE_CREATED = "knowledge.created"


class EventSource(str, Enum):
    CORE = "core"
    CLI = "cli"
    AGENT = "agent"
    SKILL = "skill"
    TOOL = "tool"
    WORKFLOW = "workflow"
    RUNTIME = "runtime"
    HANDOFF = "handoff"
    VERIFICATION = "verification"


EVENT_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:\.[a-z][a-z0-9_-]*)+$")
MAX_EVENT_BYTES = 64 * 1024

_SENSITIVE_KEYS = {
    "authorization",
    "api_key",
    "credential",
    "password",
    "private_key",
    "secret",
    "token",
}


def _sanitize(value: Any, *, depth: int = 0) -> Any:
    if depth > 8:
        raise ValueError("event payload nesting exceeds safety limit")
    if isinstance(value, Mapping):
        result: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("event payload keys must be strings")
            normalized = key.strip().lower().replace("-", "_")
            result[key] = "<redacted>" if normalized in _SENSITIVE_KEYS else _sanitize(item, depth=depth + 1)
        return result
    if isinstance(value, (list, tuple)):
        return [_sanitize(item, depth=depth + 1) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(f"event payload contains unsupported value: {type(value).__name__}")


@dataclass(frozen=True)
class Event:
    """Immutable event envelope; payload is data only and never executable."""

    name: str
    source: EventSource | str
    subject: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    correlation_id: str | None = None
    id: str = field(default_factory=lambda: uuid4().hex)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not EVENT_NAME_PATTERN.fullmatch(self.name):
            raise ValueError(f"invalid event name: {self.name!r}")
        if not self.subject.strip():
            raise ValueError("event subject must not be empty")
        sanitized = _sanitize(dict(self.payload))
        encoded = json.dumps(sanitized, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        if len(encoded.encode("utf-8")) > MAX_EVENT_BYTES:
            raise ValueError("event payload exceeds safety limit")
        if self.occurred_at.tzinfo is None:
            raise ValueError("event timestamp must be timezone-aware")
        object.__setattr__(self, "payload", MappingProxyType(sanitized))

    @property
    def event_name(self) -> str:
        return self.name

    @property
    def dangerous(self) -> bool:
        return bool(self.payload.get("dangerous", False))
