from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from uuid import uuid4


class KnowledgeKind(str, Enum):
    LANGUAGE = "language"
    FRAMEWORK = "framework"
    ECOSYSTEM = "ecosystem"
    CONCEPT = "concept"
    STANDARD = "standard"
    TOOLCHAIN = "toolchain"
    PATTERN = "pattern"


class KnowledgeStatus(str, Enum):
    UNKNOWN = "unknown"
    EXPERIMENTAL = "experimental"
    VALIDATED = "validated"
    DEPRECATED = "deprecated"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class KnowledgeSource:
    reference: str
    kind: str
    version: str | None = None
    retrieved_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.reference.strip():
            raise ValueError("Knowledge source reference must not be empty")
        if not self.kind.strip():
            raise ValueError("Knowledge source kind must not be empty")


@dataclass(frozen=True)
class KnowledgeEntry:
    name: str
    kind: KnowledgeKind
    summary: str
    topics: tuple[str, ...] = ()
    related: tuple[str, ...] = ()
    toolchains: tuple[str, ...] = ()
    versions: tuple[str, ...] = ()
    sources: tuple[KnowledgeSource, ...] = ()
    status: KnowledgeStatus = KnowledgeStatus.UNKNOWN
    confidence: float | None = None
    verification: tuple[str, ...] = ()
    id: str = field(default_factory=lambda: uuid4().hex)
    recorded_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Knowledge entry name must not be empty")
        if not self.summary.strip():
            raise ValueError("Knowledge entry summary must not be empty")
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Knowledge confidence must be between 0 and 1")
        if self.status is KnowledgeStatus.VALIDATED and (not self.sources or not self.verification):
            raise ValueError("Validated knowledge requires sources and verification criteria")
        if self.status is KnowledgeStatus.BLOCKED and self.confidence not in (None, 0.0):
            raise ValueError("Blocked knowledge must not report positive confidence")
