from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4


class ImpactLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class ImpactAssessment:
    area: str
    level: ImpactLevel
    likelihood: float
    rationale: str
    mitigations: tuple[str, ...] = ()
    id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.area.strip() or not self.rationale.strip():
            raise ValueError("Impact area and rationale must not be empty")
        if not 0.0 <= self.likelihood <= 1.0:
            raise ValueError("Impact likelihood must be between 0 and 1")


class RiskEngine:
    def assess(self, area: str, *, likelihood: float, rationale: str, mitigations: tuple[str, ...] = ()) -> ImpactAssessment:
        if likelihood >= 0.8:
            level = ImpactLevel.CRITICAL
        elif likelihood >= 0.6:
            level = ImpactLevel.HIGH
        elif likelihood >= 0.3:
            level = ImpactLevel.MEDIUM
        else:
            level = ImpactLevel.LOW
        return ImpactAssessment(area, level, likelihood, rationale, mitigations)
