from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from uuid import uuid4


class DiscoveryStatus(str, Enum):
    DISCOVERED = "discovered"
    VERIFIED = "verified"
    UNKNOWN = "unknown"
    FAILED = "failed"


@dataclass(frozen=True)
class DiscoveryFinding:
    category: str
    name: str
    value: str
    confidence: float
    source: str
    verification: tuple[str, ...] = ()
    id: str = field(default_factory=lambda: uuid4().hex)
    recorded_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.category.strip() or not self.name.strip():
            raise ValueError("Discovery finding category and name must not be empty")
        if not self.value.strip() or not self.source.strip():
            raise ValueError("Discovery finding value and source must not be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Discovery confidence must be between 0 and 1")


@dataclass(frozen=True)
class DiscoveryReport:
    root: str
    status: DiscoveryStatus
    findings: tuple[DiscoveryFinding, ...] = ()
    unknowns: tuple[str, ...] = ()
    experiments: tuple[str, ...] = ()
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.root.strip():
            raise ValueError("Discovery root must not be empty")
        if self.status is DiscoveryStatus.VERIFIED and not self.findings:
            raise ValueError("Verified discovery requires findings")
