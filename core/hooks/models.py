from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

from core.events.models import Event


class HookPhase(str, Enum):
    BEFORE = "before"
    AFTER = "after"


class HookDecision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"


HookHandler = Callable[[Event], HookDecision | None]


@dataclass(frozen=True)
class Hook:
    id: str
    events: tuple[str, ...]
    handler: HookHandler
    phase: HookPhase = HookPhase.BEFORE
    priority: int = 100
    gate: bool = False
    max_runtime_ms: int = 250

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("hook id must not be empty")
        if not self.events:
            raise ValueError("hook must subscribe to at least one event")
        if self.priority < 0:
            raise ValueError("hook priority must be non-negative")
        if self.max_runtime_ms < 1 or self.max_runtime_ms > 5_000:
            raise ValueError("hook runtime budget must be between 1 and 5000 ms")
        if not callable(self.handler):
            raise TypeError("hook handler must be callable")
        if not self.gate and self.phase is HookPhase.BEFORE:
            return
        if self.gate and self.phase is HookPhase.AFTER:
            raise ValueError("after hooks cannot be gates")
