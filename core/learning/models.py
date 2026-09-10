from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from uuid import uuid4


class ImprovementStatus(str, Enum):
    CANDIDATE = "candidate"
    EVALUATED = "evaluated"
    APPROVED = "approved"
    APPLIED = "applied"
    REJECTED = "rejected"
    ROLLED_BACK = "rolled_back"


@dataclass(frozen=True)
class EvidenceItem:
    source: str
    claim: str
    verified: bool = False
    evidence_id: str | None = None

    def __post_init__(self) -> None:
        if not self.source.strip() or not self.claim.strip():
            raise ValueError("Evidence source and claim must not be empty")


@dataclass(frozen=True)
class EvaluationResult:
    benchmark_passed: bool
    regression_passed: bool
    safety_passed: bool
    score_before: float
    score_after: float
    regressions: tuple[str, ...] = ()
    evidence: tuple[EvidenceItem, ...] = ()
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not 0.0 <= self.score_before <= 1.0 or not 0.0 <= self.score_after <= 1.0:
            raise ValueError("Evaluation scores must be between 0 and 1")
        if self.score_after < self.score_before and self.benchmark_passed:
            raise ValueError("A passing benchmark cannot report a lower score")

    @property
    def passed(self) -> bool:
        return self.benchmark_passed and self.regression_passed and self.safety_passed


@dataclass(frozen=True)
class ImprovementProposal:
    target: str
    summary: str
    rationale: str
    change_ref: str
    evidence: tuple[EvidenceItem, ...]
    requires_benchmark: bool = True
    requires_regression_test: bool = True
    status: ImprovementStatus = ImprovementStatus.CANDIDATE
    evaluation: EvaluationResult | None = None
    id: str = field(default_factory=lambda: uuid4().hex)
    version: int = 1
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        for value, label in ((self.target, "target"), (self.summary, "summary"),
                             (self.rationale, "rationale"), (self.change_ref, "change_ref")):
            if not value.strip():
                raise ValueError(f"Proposal {label} must not be empty")
        if self.version < 1:
            raise ValueError("Proposal version must be positive")
        if not self.evidence:
            raise ValueError("Improvement proposal requires evidence")
        if self.status in (ImprovementStatus.EVALUATED, ImprovementStatus.APPROVED,
                            ImprovementStatus.APPLIED) and self.evaluation is None:
            raise ValueError("Evaluated, approved, and applied proposals require evaluation")

    @property
    def verified_evidence_count(self) -> int:
        return sum(item.verified for item in self.evidence)
