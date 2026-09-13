"""Stable, transport-neutral Control API contracts."""

import uuid  # noqa: I001
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum


API_VERSION = "v1"


class RunStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class ApiError:
    code: str
    message: str
    request_id: str

    def as_dict(self) -> dict[str, str]:
        return {"error": self.code, "message": self.message, "request_id": self.request_id}


@dataclass(frozen=True)
class RunRecord:
    id: str
    action: str
    status: RunStatus
    subject: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    governance_status: str = "allow"
    evidence: tuple[str, ...] = ()
    capacity: str = "low"
    execution_target: str = "local"

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id, "action": self.action, "status": self.status.value,
            "subject": self.subject, "created_at": self.created_at.isoformat(),
            "governance_status": self.governance_status, "evidence": list(self.evidence),
            "capacity": self.capacity, "execution_target": self.execution_target,
        }


@dataclass(frozen=True)
class ApiEvent:
    id: str
    event_type: str
    subject: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, str] = field(default_factory=dict)

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id, "event_type": self.event_type, "subject": self.subject,
            "timestamp": self.timestamp.isoformat(), "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class ApiSnapshot:
    api_version: str
    service: str
    counts: tuple[tuple[str, int], ...]

    def as_dict(self) -> dict[str, object]:
        return {"api_version": self.api_version, "service": self.service, "counts": dict(self.counts)}


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"
