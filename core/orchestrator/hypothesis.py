from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4


class HypothesisStatus(str, Enum):
    PROPOSED = "proposed"
    TESTING = "testing"
    SUPPORTED = "supported"
    REFUTED = "refuted"
    INCONCLUSIVE = "inconclusive"


@dataclass(frozen=True)
class Hypothesis:
    statement: str
    rationale: str
    confidence: float = 0.5
    status: HypothesisStatus = HypothesisStatus.PROPOSED
    predictions: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.statement.strip():
            raise ValueError("Hypothesis statement must not be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Hypothesis confidence must be between 0 and 1")


class HypothesisEngine:
    """Tracks falsifiable hypotheses and updates confidence from explicit evidence."""

    def rank(self, hypotheses: tuple[Hypothesis, ...]) -> tuple[Hypothesis, ...]:
        return tuple(sorted(hypotheses, key=lambda item: (-item.confidence, item.id)))

    def update(
        self,
        hypothesis: Hypothesis,
        *,
        supported: bool,
        evidence_id: str,
        strength: float = 0.25,
    ) -> Hypothesis:
        if not evidence_id.strip():
            raise ValueError("Evidence ID must not be empty")
        if not 0.0 <= strength <= 1.0:
            raise ValueError("Evidence strength must be between 0 and 1")
        delta = strength * (1.0 - hypothesis.confidence if supported else hypothesis.confidence)
        confidence = hypothesis.confidence + delta if supported else hypothesis.confidence - delta
        status = HypothesisStatus.SUPPORTED if supported else HypothesisStatus.REFUTED
        return Hypothesis(
            statement=hypothesis.statement,
            rationale=hypothesis.rationale,
            confidence=max(0.0, min(1.0, confidence)),
            status=status,
            predictions=hypothesis.predictions,
            evidence=hypothesis.evidence + (evidence_id,),
            id=hypothesis.id,
        )
