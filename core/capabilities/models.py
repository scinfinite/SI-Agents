from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from uuid import uuid4


class CapabilityStatus(str, Enum):
    UNKNOWN = "unknown"
    EXPERIMENTAL = "experimental"
    VALIDATED = "validated"
    DEPRECATED = "deprecated"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class Capability:
    name: str
    category: str
    status: CapabilityStatus = CapabilityStatus.UNKNOWN
    agent: str | None = None
    skills: tuple[str, ...] = ()
    tools: tuple[str, ...] = ()
    permissions: tuple[str, ...] = ()
    inputs: tuple[str, ...] = ()
    outputs: tuple[str, ...] = ()
    verification: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    confidence: float | None = None
    version: str | None = None
    health: float | None = None
    benchmark_score: float | None = None
    id: str = field(default_factory=lambda: uuid4().hex)
    registered_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Capability name must not be empty")
        if not self.category.strip():
            raise ValueError("Capability category must not be empty")
        for value, label in ((self.confidence, "confidence"), (self.health, "health"), (self.benchmark_score, "benchmark_score")):
            if value is not None and not 0.0 <= value <= 1.0:
                raise ValueError(f"Capability {label} must be between 0 and 1")
        if self.status is CapabilityStatus.VALIDATED and not self.verification:
            raise ValueError("Validated capability must declare verification criteria")
        if self.status is CapabilityStatus.BLOCKED and self.health not in (None, 0.0):
            raise ValueError("Blocked capability must not report positive health")
