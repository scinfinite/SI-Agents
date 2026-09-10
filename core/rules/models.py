from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum

from core.events.models import Event


class RuleEffect(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"
    AUDIT = "audit"


@dataclass(frozen=True)
class RuleMatch:
    """Safe exact-match predicates; rules contain no executable expressions."""

    events: tuple[str, ...] = ()
    sources: tuple[str, ...] = ()
    subjects: tuple[str, ...] = ()
    payload_equals: Mapping[str, object] = field(default_factory=dict)

    def matches(self, event: Event) -> bool:
        if self.events and event.name not in self.events:
            return False
        source = event.source.value if hasattr(event.source, "value") else str(event.source)
        if self.sources and source not in self.sources:
            return False
        if self.subjects and event.subject not in self.subjects:
            return False
        return all(event.payload.get(key) == value for key, value in self.payload_equals.items())


@dataclass(frozen=True)
class Rule:
    id: str
    description: str
    match: RuleMatch
    effect: RuleEffect
    priority: int = 100
    dangerous_only: bool = False

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("rule id must not be empty")
        if not self.description.strip():
            raise ValueError("rule description must not be empty")
        if self.priority < 0:
            raise ValueError("rule priority must be non-negative")

    def matches(self, event: Event) -> bool:
        return (not self.dangerous_only or event.dangerous) and self.match.matches(event)
