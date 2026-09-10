from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4


class TaskKind(str, Enum):
    ENGINEERING = "engineering"
    DEBUGGING = "debugging"
    RESEARCH = "research"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Problem:
    description: str
    kind: TaskKind = TaskKind.ENGINEERING
    constraints: tuple[str, ...] = ()
    acceptance_criteria: tuple[str, ...] = ()
    context: tuple[str, ...] = ()
    id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.description.strip():
            raise ValueError("Problem description must not be empty")
        if not self.acceptance_criteria:
            raise ValueError("Problem must declare at least one acceptance criterion")


@dataclass(frozen=True)
class Subtask:
    description: str
    id: str = field(default_factory=lambda: uuid4().hex)
    dependencies: tuple[str, ...] = ()
    acceptance_criteria: tuple[str, ...] = ()
    rationale: str = ""

    def __post_init__(self) -> None:
        if not self.description.strip():
            raise ValueError("Subtask description must not be empty")


@dataclass(frozen=True)
class Decomposition:
    problem_id: str
    subtasks: tuple[Subtask, ...]
    strategy: str
    assumptions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        ids = {item.id for item in self.subtasks}
        if len(ids) != len(self.subtasks):
            raise ValueError("Decomposition contains duplicate subtask IDs")
        for item in self.subtasks:
            if item.id in item.dependencies:
                raise ValueError("Subtask cannot depend on itself")
            if any(dep not in ids for dep in item.dependencies):
                raise ValueError("Subtask dependency must reference a known subtask")
