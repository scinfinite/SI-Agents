from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4


class StepKind(str, Enum):
    INSPECT = "inspect"
    RESEARCH = "research"
    EXECUTE = "execute"
    TEST = "test"
    VERIFY = "verify"
    DOCUMENT = "document"


@dataclass(frozen=True)
class PlanStep:
    description: str
    kind: StepKind
    id: str = field(default_factory=lambda: uuid4().hex)
    dependencies: tuple[str, ...] = ()
    expected_evidence: tuple[str, ...] = ()
    risk: float = 0.0

    def __post_init__(self) -> None:
        if not self.description.strip():
            raise ValueError("Plan step description must not be empty")
        if not 0.0 <= self.risk <= 1.0:
            raise ValueError("Plan step risk must be between 0 and 1")


@dataclass(frozen=True)
class Plan:
    objective: str
    steps: tuple[PlanStep, ...]
    success_criteria: tuple[str, ...]
    assumptions: tuple[str, ...] = ()
    id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.objective.strip():
            raise ValueError("Plan objective must not be empty")
        if not self.steps:
            raise ValueError("Plan must contain at least one step")
        if not self.success_criteria:
            raise ValueError("Plan must declare success criteria")
        ids = {step.id for step in self.steps}
        if len(ids) != len(self.steps):
            raise ValueError("Plan contains duplicate step IDs")
        for step in self.steps:
            if any(dep not in ids for dep in step.dependencies):
                raise ValueError("Plan dependency must reference a known step")
            if step.id in step.dependencies:
                raise ValueError("Plan step cannot depend on itself")
