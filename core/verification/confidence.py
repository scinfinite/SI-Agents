from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ConfidenceLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


def level_for(value: float) -> ConfidenceLevel:
    if not 0.0 <= value <= 1.0:
        raise ValueError("Confidence must be between 0 and 1")
    if value < 0.5:
        return ConfidenceLevel.LOW
    if value < 0.8:
        return ConfidenceLevel.MEDIUM
    return ConfidenceLevel.HIGH


@dataclass(frozen=True)
class ConfidenceAssessment:
    value: float
    level: ConfidenceLevel
    rationale: str

    def __post_init__(self) -> None:
        if not 0.0 <= self.value <= 1.0:
            raise ValueError("Confidence must be between 0 and 1")
        if not self.rationale.strip():
            raise ValueError("Confidence rationale must not be empty")
        if self.level is not level_for(self.value):
            raise ValueError("Confidence level does not match value")


def assess(value: float, rationale: str) -> ConfidenceAssessment:
    return ConfidenceAssessment(value=value, level=level_for(value), rationale=rationale)
