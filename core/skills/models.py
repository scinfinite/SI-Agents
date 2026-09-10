from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4


class SkillStatus(str, Enum):
    EXPERIMENTAL = "experimental"
    VALIDATED = "validated"
    DEPRECATED = "deprecated"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class Skill:
    name: str
    category: str
    procedure: tuple[str, ...]
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    required_tools: tuple[str, ...] = ()
    required_permissions: tuple[str, ...] = ()
    safety_constraints: tuple[str, ...] = ()
    verification: tuple[str, ...] = ()
    failure_handling: tuple[str, ...] = ()
    success_criteria: tuple[str, ...] = ()
    status: SkillStatus = SkillStatus.EXPERIMENTAL
    version: str = "1"
    id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.category.strip():
            raise ValueError("Skill name and category are required")
        if not self.procedure:
            raise ValueError("Skill must declare a procedure")
        if not self.inputs or not self.outputs:
            raise ValueError("Skill must declare inputs and outputs")
        if not self.success_criteria:
            raise ValueError("Skill must declare success criteria")
        if self.status is SkillStatus.VALIDATED:
            if not self.verification:
                raise ValueError("Validated skills must declare verification criteria")
            if not self.failure_handling:
                raise ValueError("Validated skills must declare failure handling")


@dataclass(frozen=True)
class SkillResult:
    skill_id: str
    status: str
    outputs: dict[str, object]
    verification: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    error: str | None = None
