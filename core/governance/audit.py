"""Append-only in-memory audit records for governance decisions."""

from dataclasses import dataclass
from datetime import UTC, datetime

from core.governance.models import Decision, DecisionStatus


@dataclass(frozen=True)
class AuditRecord:
    action: str
    status: DecisionStatus
    effective_risk: str
    reasons: tuple[str, ...]
    recorded_at: datetime


class AuditLog:
    """Keep decision evidence without storing request payloads or secrets."""

    def __init__(self) -> None:
        self._records: list[AuditRecord] = []

    def record(self, decision: Decision) -> AuditRecord:
        record = AuditRecord(
            action=decision.request.action,
            status=decision.status,
            effective_risk=decision.effective_risk.value,
            reasons=decision.reasons,
            recorded_at=datetime.now(UTC),
        )
        self._records.append(record)
        return record

    def records(self) -> tuple[AuditRecord, ...]:
        return tuple(self._records)
