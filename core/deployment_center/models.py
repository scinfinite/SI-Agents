"""Typed deployment planning contracts.

These objects describe desired deployment state only. They never grant authority,
move credentials, or execute a harness.
"""

from dataclasses import dataclass
from enum import StrEnum


class DeploymentState(StrEnum):
    DRAFT = "draft"
    VALID = "valid"
    BLOCKED = "blocked"
    APPLIED = "applied"


@dataclass(frozen=True, slots=True)
class HarnessTarget:
    id: str
    version: str
    adapter_path: str
    enabled: bool = False

    def __post_init__(self) -> None:
        if not self.id.strip() or not self.version.strip() or not self.adapter_path.strip():
            raise ValueError("harness target requires id, version, and adapter_path")

    def as_dict(self) -> dict[str, object]:
        return {"id": self.id, "version": self.version, "adapter_path": self.adapter_path, "enabled": self.enabled}


@dataclass(frozen=True, slots=True)
class DeploymentPlan:
    id: str
    harness_id: str
    agents: tuple[str, ...]
    teams: tuple[str, ...]
    skills: tuple[str, ...]
    requested_capabilities: tuple[str, ...]
    requested_permissions: tuple[str, ...]
    state: DeploymentState
    reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.id.strip() or not self.harness_id.strip():
            raise ValueError("deployment id and harness_id are required")
        for name, values in (("agents", self.agents), ("teams", self.teams), ("skills", self.skills),
                             ("requested_capabilities", self.requested_capabilities),
                             ("requested_permissions", self.requested_permissions)):
            if any(not value.strip() for value in values):
                raise ValueError(f"{name} cannot contain empty identifiers")
            if len(set(values)) != len(values):
                raise ValueError(f"{name} must contain unique identifiers")

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id, "harness_id": self.harness_id, "agents": list(self.agents),
            "teams": list(self.teams), "skills": list(self.skills),
            "requested_capabilities": list(self.requested_capabilities),
            "requested_permissions": list(self.requested_permissions),
            "state": self.state.value, "reasons": list(self.reasons),
        }
