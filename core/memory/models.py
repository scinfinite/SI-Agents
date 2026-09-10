from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from uuid import uuid4


class MemoryScope(str, Enum):
    TASK = "task"
    PROJECT = "project"
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

    def __post_init__(self) -> None:
        if not self.source.strip() or not self.claim.strip():
            raise ValueError("Memory evidence requires source and claim")


@dataclass(frozen=True)
class MemoryEntry:
    content: str
    memory_type: MemoryType
    scope: MemoryScope
    project_id: str | None = None
    task_id: str | None = None
    tags: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()
    evidence: tuple[MemoryEvidence, ...] = ()
    confidence: float = 0.0
    status: MemoryStatus = MemoryStatus.CANDIDATE
    supersedes: str | None = None
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
        if self.scope is MemoryScope.PROJECT and not self.project_id:
            raise ValueError("Project memory requires project_id")
        if self.scope is MemoryScope.TASK and not self.task_id:
            raise ValueError("Task memory requires task_id")
        if self.version < 1:
            raise ValueError("Memory version must be positive")
        if self.expires_at is not None and self.expires_at <= self.created_at:
            raise ValueError("Memory expiry must be after creation")

    def is_expired(self, now: datetime | None = None) -> bool:
        return self.expires_at is not None and self.expires_at <= (now or datetime.now(UTC))


@dataclass(frozen=True)
class PromotionDecision:
    memory_id: str
    allowed: bool
    target_scope: MemoryScope
    reasons: tuple[str, ...] = ()
    required_evidence: int = 0
    verified_evidence: int = 0
