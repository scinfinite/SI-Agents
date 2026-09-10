"""Harness-neutral deployment manifests.

A deployment manifest describes what an adapter may expose. It never grants
permissions, enables a harness, or executes an agent.
"""

from dataclasses import dataclass

from core.organization.models import AgentDefinition
from core.teams.models import TeamDefinition


@dataclass(frozen=True)
class HarnessDeploymentManifest:
    """Portable organization surface consumed by a harness installer/adapter."""

    protocol: str
    harness_id: str
    agents: tuple[str, ...]
    teams: tuple[str, ...]
    skills: tuple[str, ...]
    required_permissions: tuple[str, ...]
    capabilities: tuple[str, ...]

    def __post_init__(self) -> None:
        for name, values in (("agents", self.agents), ("teams", self.teams), ("skills", self.skills)):
            if any(not value.strip() for value in values):
                raise ValueError(f"{name} cannot contain empty identifiers")
            if len(set(values)) != len(values):
                raise ValueError(f"{name} must contain unique identifiers")
        if not self.harness_id.strip() or not self.protocol.strip():
            raise ValueError("protocol and harness_id are required")

    def as_dict(self) -> dict[str, object]:
        return {
            "protocol": self.protocol,
            "harness_id": self.harness_id,
            "agents": list(self.agents),
            "teams": list(self.teams),
            "skills": list(self.skills),
            "required_permissions": list(self.required_permissions),
            "capabilities": list(self.capabilities),
        }


def build_manifest(
    harness_id: str,
    agents: tuple[AgentDefinition, ...],
    teams: tuple[TeamDefinition, ...],
    *,
    skills: tuple[str, ...] = (),
    capabilities: tuple[str, ...] = (),
    protocol: str = "si.runtime.v1",
) -> HarnessDeploymentManifest:
    """Build a deterministic exposure manifest without changing authority."""
    agent_ids = tuple(sorted(agent.id for agent in agents))
    team_ids = tuple(sorted(team.id for team in teams))
    permissions = tuple(
        sorted({permission for agent in agents for permission in agent.permissions})
    )
    return HarnessDeploymentManifest(
        protocol=protocol,
        harness_id=harness_id,
        agents=agent_ids,
        teams=team_ids,
        skills=tuple(sorted(skills)),
        required_permissions=permissions,
        capabilities=tuple(sorted(set(capabilities))),
    )
