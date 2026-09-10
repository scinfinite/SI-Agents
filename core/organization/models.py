from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class AgentStatus(StrEnum):
    CATALOGED = "cataloged"
    IMPLEMENTED = "implemented"
    EXPERIMENTAL = "experimental"
    DEPRECATED = "deprecated"


@dataclass(frozen=True)
class Division:
    id: str
    name: str
    description: str

    def __post_init__(self) -> None:
        _require_id(self.id, "division id")
        if not self.name.strip() or not self.description.strip():
            raise ValueError("Division name and description are required")


@dataclass(frozen=True)
class AgentDefinition:
    id: str
    name: str
    division: str
    description: str
    responsibilities: tuple[str, ...]
    deliverables: tuple[str, ...]
    success_criteria: tuple[str, ...]
    boundaries: tuple[str, ...]
    skills: tuple[str, ...] = ()
    capabilities: tuple[str, ...] = ()
    permissions: tuple[str, ...] = ()
    harnesses: tuple[str, ...] = ()
    environments: tuple[str, ...] = ()
    status: AgentStatus = AgentStatus.CATALOGED
    implementation: str | None = None

    def __post_init__(self) -> None:
        _require_id(self.id, "agent id")
        if not self.name.strip() or not self.division.strip() or not self.description.strip():
            raise ValueError("Agent identity, division, and description are required")
        for field_name in ("responsibilities", "deliverables", "success_criteria", "boundaries"):
            if not getattr(self, field_name):
                raise ValueError(f"Agent must declare {field_name}")
        for field_name in ("skills", "capabilities", "permissions", "harnesses", "environments"):
            values = getattr(self, field_name)
            if len(values) != len(set(values)):
                raise ValueError(f"Agent {self.id} has duplicate {field_name}")


def _require_id(value: str, label: str) -> None:
    if not value or value != value.strip() or any(char not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for char in value):
        raise ValueError(f"Invalid {label}: {value!r}")
