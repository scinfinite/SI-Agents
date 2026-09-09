from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from uuid import uuid4


class VerificationStatus(str, Enum):
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    FAILED = "failed"


@dataclass(frozen=True)
class Evidence:
    claim: str
    source: str
    verification_status: VerificationStatus
    details: str = ""
    id: str = uuid4().hex
    recorded_at: datetime = datetime.now(UTC)

    def __post_init__(self) -> None:
        if not self.claim.strip():
            raise ValueError("Evidence claim must not be empty")
        if not self.source.strip():
            raise ValueError("Evidence source must not be empty")
        if not self.details.strip() and self.verification_status is VerificationStatus.FAILED:
            raise ValueError("Failed evidence must include details")
