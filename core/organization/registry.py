from __future__ import annotations

from core.organization.models import AgentDefinition, AgentStatus, Division


class AgentCatalog:
    """Canonical in-memory view of divisions and declarative agent definitions."""

    def __init__(self) -> None:
        self._divisions: dict[str, Division] = {}
        self._agents: dict[str, AgentDefinition] = {}

    def register_division(self, division: Division) -> Division:
        if division.id in self._divisions:
            raise ValueError(f"Duplicate division id: {division.id}")
        self._divisions[division.id] = division
        return division

    def register(self, agent: AgentDefinition) -> AgentDefinition:
        if agent.id in self._agents:
            raise ValueError(f"Duplicate agent id: {agent.id}")
        if agent.division not in self._divisions:
            raise ValueError(f"Unknown division for agent {agent.id}: {agent.division}")
        if any(existing.name == agent.name for existing in self._agents.values()):
            raise ValueError(f"Duplicate agent name: {agent.name}")
        self._agents[agent.id] = agent
        return agent

    def division(self, division_id: str) -> Division:
        try:
            return self._divisions[division_id]
        except KeyError as exc:
            raise KeyError(f"Unknown division: {division_id}") from exc

    def get(self, agent_id: str) -> AgentDefinition:
        try:
            return self._agents[agent_id]
        except KeyError as exc:
            raise KeyError(f"Unknown agent: {agent_id}") from exc

    def all_divisions(self) -> tuple[Division, ...]:
        return tuple(self._divisions.values())

    def all(self) -> tuple[AgentDefinition, ...]:
        return tuple(self._agents.values())

    def by_division(self, division_id: str) -> tuple[AgentDefinition, ...]:
        self.division(division_id)
        return tuple(agent for agent in self._agents.values() if agent.division == division_id)

    def select(
        self,
        *,
        division: str | None = None,
        required_skills: tuple[str, ...] = (),
        required_capabilities: tuple[str, ...] = (),
        required_permissions: tuple[str, ...] = (),
        harness: str | None = None,
        environment: str | None = None,
        statuses: tuple[AgentStatus, ...] = (AgentStatus.CATALOGED, AgentStatus.IMPLEMENTED),
    ) -> tuple[AgentDefinition, ...]:
        if division is not None:
            self.division(division)
        allowed = set(statuses)
        return tuple(
            agent
            for agent in self._agents.values()
            if agent.status in allowed
            and (division is None or agent.division == division)
            and set(required_skills).issubset(agent.skills)
            and set(required_capabilities).issubset(agent.capabilities)
            and set(required_permissions).issubset(agent.permissions)
            and (harness is None or harness in agent.harnesses)
            and (environment is None or environment in agent.environments)
        )

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self._divisions:
            errors.append("catalog contains no divisions")
        if not self._agents:
            errors.append("catalog contains no agents")
        for agent in self._agents.values():
            if agent.division not in self._divisions:
                errors.append(f"agent {agent.id} references missing division {agent.division}")
            if agent.status is AgentStatus.IMPLEMENTED and not agent.implementation:
                errors.append(f"implemented agent {agent.id} must declare implementation")
        return tuple(errors)
