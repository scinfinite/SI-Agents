from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from uuid import uuid4


class MemoryScope(str, Enum):
    TASK = "task"
    PROJECT = "project"
    TEAM = "team"
    AGENT = "agent"
    DIVISION = "division"
    ORGANIZATION = "organization"
    GLOBAL = "global"


class MemoryType(str, Enum):
    FACT = "fact"
    DECISION = "decision"
    LESSON = "lesson"
    PROCEDURE = "procedure"
    PREFERENCE = "preference"
    FAILURE = "failure"


class MemoryStatus(str, Enum):
    CANDIDATE = "candidate"
    VALIDATED = "validated"
    PROMOTED = "promoted"
    EXPIRED = "expired"
    REJECTED = "rejected"


@dataclass(frozen=True)
class MemoryEvidence:
    source: str
    claim: str
    verified: bool = False
    evidence_id: str | None = None
    captured_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.source.strip() or not self.claim.strip():
            raise ValueError("Memory evidence requires source and claim")
        if self.captured_at.tzinfo is None:
            raise ValueError("Memory evidence timestamp must be timezone-aware")


@dataclass(frozen=True)
class MemoryEntry:
    content: str
    memory_type: MemoryType
    scope: MemoryScope
    project_id: str | None = None
    task_id: str | None = None
    team_id: str | None = None
    agent_id: str | None = None
    division_id: str | None = None
    organization_id: str | None = None
    tags: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()
    evidence: tuple[MemoryEvidence, ...] = ()
    confidence: float = 0.0
    status: MemoryStatus = MemoryStatus.CANDIDATE
    supersedes: str | None = None
    contradicts: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    id: str = field(default_factory=lambda: str(uuid4()))
    version: int = 1

    def __post_init__(self) -> None:
        if not self.content.strip():
            raise ValueError("Memory content must not be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Memory confidence must be between 0 and 1")
        if not self.provenance:
            raise ValueError("Memory requires provenance")
        required = {
            MemoryScope.TASK: self.task_id,
            MemoryScope.PROJECT: self.project_id,
            MemoryScope.TEAM: self.team_id,
            MemoryScope.AGENT: self.agent_id,
            MemoryScope.DIVISION: self.division_id,
            MemoryScope.ORGANIZATION: self.organization_id,
        }
        if self.scope in required and not required[self.scope]:
            raise ValueError(f"{self.scope.value} memory requires its scope id")
        if self.version < 1:
            raise ValueError("Memory version must be positive")
        if self.created_at.tzinfo is None:
            raise ValueError("Memory timestamp must be timezone-aware")
        if self.expires_at is not None and self.expires_at <= self.created_at:
            raise ValueError("Memory expiry must be after creation")

    def is_expired(self, now: datetime | None = None) -> bool:
        return self.expires_at is not None and self.expires_at <= (now or datetime.now(UTC))

    def scope_id(self) -> str | None:
        return {
            MemoryScope.TASK: self.task_id,
            MemoryScope.PROJECT: self.project_id,
            MemoryScope.TEAM: self.team_id,
            MemoryScope.AGENT: self.agent_id,
            MemoryScope.DIVISION: self.division_id,
            MemoryScope.ORGANIZATION: self.organization_id,
            MemoryScope.GLOBAL: None,
        }[self.scope]


@dataclass(frozen=True)
class KnowledgeEntry:
    """Validated, source-backed knowledge; retrieval never implies proof."""

    subject: str
    claim: str
    source: str
    evidence: tuple[MemoryEvidence, ...] = ()
    confidence: float = 0.0
    tags: tuple[str, ...] = ()
    supersedes: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    id: str = field(default_factory=lambda: str(uuid4()))
    version: int = 1

    def __post_init__(self) -> None:
        if not self.subject.strip() or not self.claim.strip() or not self.source.strip():
            raise ValueError("Knowledge requires subject, claim, and source")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Knowledge confidence must be between 0 and 1")
        if not self.evidence or not all(item.verified for item in self.evidence):
            raise ValueError("Knowledge requires at least one verified evidence item")
        if self.created_at.tzinfo is None:
            raise ValueError("Knowledge timestamp must be timezone-aware")
        if self.version < 1:
            raise ValueError("Knowledge version must be positive")


@dataclass(frozen=True)
class PromotionDecision:
    memory_id: str
    allowed: bool
    target_scope: MemoryScope
    reasons: tuple[str, ...] = ()
    required_evidence: int = 0
    verified_evidence: int = 0
