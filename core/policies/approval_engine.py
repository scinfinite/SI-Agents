from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from uuid import uuid4


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class ApprovalRequest:
    task_id: str
    capability: str
    reason: str
    id: str = field(default_factory=lambda: uuid4().hex)
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    decided_at: datetime | None = None


class ApprovalEngine:
    """Track high-risk approvals separately from permission evaluation."""

    def __init__(self) -> None:
        self._requests: dict[str, ApprovalRequest] = {}

    def request(self, task_id: str, capability: str, reason: str) -> ApprovalRequest:
        if not task_id.strip() or not capability.strip() or not reason.strip():
            raise ValueError("Approval task, capability, and reason are required")
        request = ApprovalRequest(task_id=task_id, capability=capability, reason=reason)
        self._requests[request.id] = request
        return request

    def get(self, request_id: str) -> ApprovalRequest:
        try:
            return self._requests[request_id]
        except KeyError as exc:
            raise KeyError(f"Unknown approval request: {request_id}") from exc

    def approve(self, request_id: str) -> ApprovalRequest:
        return self._decide(request_id, ApprovalStatus.APPROVED)

    def reject(self, request_id: str) -> ApprovalRequest:
        return self._decide(request_id, ApprovalStatus.REJECTED)

    def pending(self) -> tuple[ApprovalRequest, ...]:
        return tuple(item for item in self._requests.values() if item.status is ApprovalStatus.PENDING)

    def _decide(self, request_id: str, status: ApprovalStatus) -> ApprovalRequest:
        request = self.get(request_id)
        if request.status is not ApprovalStatus.PENDING:
            raise ValueError(f"Approval request already decided: {request_id}")
        request.status = status
        request.decided_at = datetime.now(UTC)
        return request
