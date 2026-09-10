from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4


class ReasoningType(str, Enum):
    DEDUCTIVE = "deductive"
    INDUCTIVE = "inductive"
    ABDUCTIVE = "abductive"
    CAUSAL = "causal"
    COMPARATIVE = "comparative"


@dataclass(frozen=True)
class ReasoningStep:
    premise: str
    inference: str
    conclusion: str
    reasoning_type: ReasoningType
    evidence: tuple[str, ...] = ()
    confidence: float = 0.5
    id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not all(value.strip() for value in (self.premise, self.inference, self.conclusion)):
            raise ValueError("Reasoning fields must not be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Reasoning confidence must be between 0 and 1")


class ReasoningEngine:
    def chain(self, steps: tuple[ReasoningStep, ...]) -> float:
        if not steps:
            raise ValueError("Reasoning chain requires at least one step")
        confidence = 1.0
        for step in steps:
            confidence *= step.confidence
        return confidence

    def strongest(self, steps: tuple[ReasoningStep, ...]) -> ReasoningStep:
        if not steps:
            raise ValueError("Reasoning chain requires at least one step")
        return max(steps, key=lambda step: (step.confidence, step.id))
