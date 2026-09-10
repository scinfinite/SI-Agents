from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from uuid import uuid4


class VerificationStatus(str, Enum):
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    FAILED = "failed"


class EvidenceKind(str, Enum):
    TEST = "test"
    BUILD = "build"
    STATIC_ANALYSIS = "static_analysis"
    RUNTIME = "runtime"
    SECURITY = "security"
    RED_TEAM = "red_team"
    REGRESSION = "regression"
    RESEARCH = "research"
    REVIEW = "review"
    OTHER = "other"


@dataclass(frozen=True)
class Evidence:
    claim: str
    source: str
    verification_status: VerificationStatus
    details: str = ""
    kind: EvidenceKind = EvidenceKind.OTHER
    task_id: str | None = None
    id: str = field(default_factory=lambda: uuid4().hex)
    recorded_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.claim.strip():
            raise ValueError("Evidence claim must not be empty")
        if not self.source.strip():
            raise ValueError("Evidence source must not be empty")
        if self.task_id is not None and not self.task_id.strip():
            raise ValueError("Evidence task ID must not be blank")
        if not self.details.strip() and self.verification_status is VerificationStatus.FAILED:
            raise ValueError("Failed evidence must include details")
