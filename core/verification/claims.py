from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4


@dataclass(frozen=True)
class Claim:
    """A bounded statement whose truth must be established by evidence."""

    statement: str
    scope: str
    acceptance_criteria: tuple[str, ...]
    evidence_ids: tuple[str, ...] = ()
    confidence: float = 0.0
    id: str = field(default_factory=lambda: uuid4().hex)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.statement.strip():
            raise ValueError("Claim statement must not be empty")
        if not self.scope.strip():
            raise ValueError("Claim scope must not be empty")
        if not self.acceptance_criteria or any(not item.strip() for item in self.acceptance_criteria):
            raise ValueError("Claim must include non-empty acceptance criteria")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Claim confidence must be between 0 and 1")
        if len(set(self.evidence_ids)) != len(self.evidence_ids):
            raise ValueError("Claim evidence IDs must be unique")
