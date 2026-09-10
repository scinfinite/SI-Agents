from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
import re


class SkillStatus(str, Enum):
    EXPERIMENTAL = "experimental"
    VALIDATED = "validated"
    DEPRECATED = "deprecated"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class SkillRequirement:
    name: str
    kind: str
    version: str = "*"


@dataclass(frozen=True)
class Skill:
    schema: str
    version: str
    id: str
    name: str
    category: str
    purpose: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    prerequisites: tuple[str, ...]
    procedure: tuple[str, ...]
    required_tools: tuple[str, ...]
    requested_capabilities: tuple[str, ...]
    requested_permissions: tuple[str, ...]
    verification: tuple[str, ...]
    failure_behavior: tuple[str, ...]
    evidence_requirements: tuple[str, ...]
    examples: tuple[str, ...]
    compatibility: tuple[SkillRequirement, ...]
    provenance: str
    status: SkillStatus = SkillStatus.EXPERIMENTAL
    dependencies: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.schema != "si-agents.skill.v1":
            raise ValueError(f"Unsupported skill schema: {self.schema!r}")
        parts = self.version.split(".")
        if not parts or any(not part.isdigit() for part in parts) or len(parts) > 3:
            raise ValueError(f"Invalid skill version: {self.version!r}")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", self.id):
            raise ValueError(f"Invalid skill id: {self.id!r}")
        if not self.name.strip() or not self.category.strip() or not self.purpose.strip():
            raise ValueError("Skill identity, category, and purpose are required")
        for field_name in ("inputs", "outputs", "prerequisites", "procedure", "verification", "failure_behavior", "evidence_requirements", "examples"):
            if not getattr(self, field_name):
                raise ValueError(f"Skill requires non-empty {field_name}")
        if self.status is SkillStatus.VALIDATED and not self.provenance.strip():
            raise ValueError("Validated skills require provenance")

    def as_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["status"] = self.status.value
        data["compatibility"] = [asdict(item) for item in self.compatibility]
        return data

    @property
    def major_version(self) -> int:
        return int(self.version.split(".", 1)[0])


@dataclass(frozen=True)
class SkillResult:
    skill_id: str
    status: str
    outputs: dict[str, object]
    verification: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    error: str | None = None
