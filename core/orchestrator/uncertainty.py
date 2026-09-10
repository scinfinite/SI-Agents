from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4


class UncertaintyLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Uncertainty:
    statement: str
    level: UncertaintyLevel
    confidence: float
    assumptions: tuple[str, ...] = ()
    missing_evidence: tuple[str, ...] = ()
    id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.statement.strip():
            raise ValueError("Uncertainty statement must not be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Uncertainty confidence must be between 0 and 1")


class UncertaintyEngine:
    def assess(
        self,
        statement: str,
        *,
        evidence_count: int,
        assumptions: tuple[str, ...] = (),
        missing_evidence: tuple[str, ...] = (),
    ) -> Uncertainty:
        if evidence_count < 0:
            raise ValueError("Evidence count must not be negative")
        if not statement.strip():
            raise ValueError("Uncertainty statement must not be empty")
        if not evidence_count and not assumptions:
            level = UncertaintyLevel.UNKNOWN
            confidence = 0.0
        elif missing_evidence or assumptions:
            level = UncertaintyLevel.MEDIUM
            confidence = min(0.75, 0.4 + (0.1 * evidence_count))
        else:
            level = UncertaintyLevel.LOW
            confidence = min(0.95, 0.6 + (0.1 * evidence_count))
        return Uncertainty(statement, level, confidence, assumptions, missing_evidence)
