"""Typed, deterministic agent/team definitions and builders for V4 Phase 49."""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field

from core.runtime.omniroute import OmniRoutePolicy


_NAME = re.compile(r"^[a-z][a-z0-9._-]{1,63}$")
SCHEMA_VERSION = 1


class BuilderError(ValueError):
    """Invalid agent/team definition or composition."""


@dataclass(frozen=True)
class ResourceLimits:
    """Declarative execution limits; enforcement belongs to later runtime policy layers."""

    timeout_seconds: float = 900.0
    max_parallel: int = 1
    max_tokens: int | None = None
    max_cost: float | None = None

    def __post_init__(self) -> None:
        if self.timeout_seconds <= 0 or self.max_parallel <= 0:
            raise BuilderError("resource limits must be positive")
        if self.max_tokens is not None and self.max_tokens <= 0:
            raise BuilderError("max_tokens must be positive")
        if self.max_cost is not None and self.max_cost < 0:
            raise BuilderError("max_cost must be non-negative")


@dataclass(frozen=True)
class AgentDefinition:
    """Immutable SI-native agent definition suitable for registry/catalog storage."""

    agent_id: str
    role: str
    description: str
    skills: tuple[str, ...] = ()
    capabilities: tuple[str, ...] = ()
    model_policy: OmniRoutePolicy = field(default_factory=OmniRoutePolicy)
    resources: ResourceLimits = field(default_factory=ResourceLimits)
    boundaries: tuple[str, ...] = ()
    evidence_required: bool = True
    metadata: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not _NAME.fullmatch(self.agent_id):
            raise BuilderError("agent_id must be 2-64 chars of lowercase letters, digits, '.', '_' or '-'")
        if not self.role.strip() or not self.description.strip():
            raise BuilderError("agent role and description are required")
        for field_name, values in (("skills", self.skills), ("capabilities", self.capabilities), ("boundaries", self.boundaries)):
            if any(not value.strip() for value in values):
                raise BuilderError(f"{field_name} cannot contain empty values")
            if len(set(values)) != len(values):
                raise BuilderError(f"{field_name} must be unique")
        if len({key for key, _ in self.metadata}) != len(self.metadata):
            raise BuilderError("metadata keys must be unique")
        if any(not key.strip() or not value.strip() for key, value in self.metadata):
            raise BuilderError("metadata keys and values must not be empty")

    def canonical(self) -> dict[str, object]:
        return {
            "schema_version": SCHEMA_VERSION,
            "agent_id": self.agent_id,
            "role": self.role,
            "description": self.description,
            "skills": sorted(self.skills),
            "capabilities": sorted(self.capabilities),
            "model_policy": {
                "required_capabilities": sorted(self.model_policy.required_capabilities),
                "preferred_models": list(self.model_policy.preferred_models),
                "fallback_models": list(self.model_policy.fallback_models),
                "max_input_cost": self.model_policy.max_input_cost,
                "max_output_cost": self.model_policy.max_output_cost,
            },
            "resources": {
                "timeout_seconds": self.resources.timeout_seconds,
                "max_parallel": self.resources.max_parallel,
                "max_tokens": self.resources.max_tokens,
                "max_cost": self.resources.max_cost,
            },
            "boundaries": sorted(self.boundaries),
            "evidence_required": self.evidence_required,
            "metadata": sorted(self.metadata),
        }


@dataclass(frozen=True)
class TeamDefinition:
    """Immutable composition of agents with deterministic, acyclic handoff topology."""

    team_id: str
    description: str
    members: tuple[str, ...]
    handoffs: tuple[tuple[str, str], ...] = ()
    max_parallel: int = 1
    evidence_required: bool = True
    metadata: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not _NAME.fullmatch(self.team_id):
            raise BuilderError("team_id must be 2-64 chars of lowercase letters, digits, '.', '_' or '-'")
        if not self.description.strip() or not self.members:
            raise BuilderError("team description and members are required")
        if len(set(self.members)) != len(self.members):
            raise BuilderError("team members must be unique")
        if any(not _NAME.fullmatch(member) for member in self.members):
            raise BuilderError("team members must use valid agent identifiers")
        if self.max_parallel <= 0:
            raise BuilderError("team max_parallel must be positive")
        if len(set(self.handoffs)) != len(self.handoffs):
            raise BuilderError("team handoffs must be unique")
        for source, target in self.handoffs:
            if source == target:
                raise BuilderError("team handoff cannot target itself")
            if source not in self.members or target not in self.members:
                raise BuilderError("team handoffs must reference team members")
        if _has_cycle(self.members, self.handoffs):
            raise BuilderError("team handoffs must form an acyclic graph")
        if len({key for key, _ in self.metadata}) != len(self.metadata):
            raise BuilderError("metadata keys must be unique")
        if any(not key.strip() or not value.strip() for key, value in self.metadata):
            raise BuilderError("metadata keys and values must not be empty")

    def canonical(self) -> dict[str, object]:
        return {
            "schema_version": SCHEMA_VERSION,
            "team_id": self.team_id,
            "description": self.description,
            "members": sorted(self.members),
            "handoffs": sorted(self.handoffs),
            "max_parallel": self.max_parallel,
            "evidence_required": self.evidence_required,
            "metadata": sorted(self.metadata),
        }


class AgentRegistry:
    """In-memory immutable-by-value registry with deterministic catalog output."""

    def __init__(self, agents: tuple[AgentDefinition, ...] = ()) -> None:
        self._agents: dict[str, AgentDefinition] = {}
        for agent in agents:
            self.register(agent)

    def register(self, agent: AgentDefinition) -> None:
        existing = self._agents.get(agent.agent_id)
        if existing is not None and existing != agent:
            raise BuilderError(f"agent id already registered: {agent.agent_id}")
        self._agents[agent.agent_id] = agent

    def get(self, agent_id: str) -> AgentDefinition:
        try:
            return self._agents[agent_id]
        except KeyError as exc:
            raise BuilderError(f"unknown agent: {agent_id}") from exc

    def list(self) -> tuple[AgentDefinition, ...]:
        return tuple(self._agents[key] for key in sorted(self._agents))

    def catalog(self) -> dict[str, object]:
        agents = [agent.canonical() for agent in self.list()]
        encoded = _canonical_json(agents)
        return {
            "schema_version": SCHEMA_VERSION,
            "agents": agents,
            "catalog_sha256": hashlib.sha256(encoded.encode()).hexdigest(),
        }

    def digest(self) -> str:
        return str(self.catalog()["catalog_sha256"])


class TeamBuilder:
    """Compose teams while preventing undeclared agents/capabilities and cyclic handoffs."""

    def __init__(self, registry: AgentRegistry) -> None:
        self.registry = registry

    def build(
        self,
        team_id: str,
        description: str,
        members: tuple[str, ...],
        *,
        handoffs: tuple[tuple[str, str], ...] = (),
        max_parallel: int = 1,
        evidence_required: bool = True,
        metadata: tuple[tuple[str, str], ...] = (),
    ) -> TeamDefinition:
        team = TeamDefinition(team_id, description, members, handoffs, max_parallel, evidence_required, metadata)
        for member in team.members:
            self.registry.get(member)
        return team

    def capabilities(self, team: TeamDefinition) -> tuple[str, ...]:
        capabilities: set[str] = set()
        for member in team.members:
            capabilities.update(self.registry.get(member).capabilities)
        return tuple(sorted(capabilities))

    def effective_parallelism(self, team: TeamDefinition) -> int:
        member_limit = sum(self.registry.get(member).resources.max_parallel for member in team.members)
        return min(team.max_parallel, max(1, member_limit))

    def execution_layers(self, team: TeamDefinition) -> tuple[tuple[str, ...], ...]:
        """Return deterministic parallel layers implied by the handoff DAG."""
        members = set(team.members)
        predecessors = {member: set() for member in members}
        for source, target in team.handoffs:
            predecessors[target].add(source)
        layers: list[tuple[str, ...]] = []
        remaining = set(members)
        while remaining:
            ready = tuple(sorted(member for member in remaining if not (predecessors[member] & remaining)))
            if not ready:
                raise BuilderError("team handoffs contain an execution cycle")
            layers.append(ready)
            remaining.difference_update(ready)
        return tuple(layers)

    def manifest(self, team: TeamDefinition) -> dict[str, object]:
        members = [self.registry.get(member).canonical() for member in sorted(team.members)]
        payload = {
            "schema_version": SCHEMA_VERSION,
            "team": team.canonical(),
            "members": members,
            "capabilities": list(self.capabilities(team)),
            "execution_layers": [list(layer) for layer in self.execution_layers(team)],
        }
        encoded = _canonical_json(payload)
        return {**payload, "manifest_sha256": hashlib.sha256(encoded.encode()).hexdigest()}


def _has_cycle(members: tuple[str, ...], handoffs: tuple[tuple[str, str], ...]) -> bool:
    graph = {member: [] for member in members}
    for source, target in handoffs:
        graph[source].append(target)
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        if any(visit(child) for child in graph[node]):
            return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(member) for member in members)


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


__all__ = [
    "AgentDefinition", "AgentRegistry", "BuilderError", "ResourceLimits", "TeamBuilder", "TeamDefinition",
]
