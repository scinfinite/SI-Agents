from __future__ import annotations

from core.orchestrator.context_manager import TaskContext

from collections.abc import Callable


AgentWorker = Callable[[str, TaskContext], str]


class AgentCoordinator:
    """Coordinate named agent workers without granting them implicit permissions."""

    def __init__(self) -> None:
        self._agents: dict[str, AgentWorker] = {}

    def register(self, name: str, worker: AgentWorker) -> None:
        normalized = name.strip()
        if not normalized:
            raise ValueError("Agent name must not be empty")
        if normalized in self._agents:
            raise ValueError(f"Agent already registered: {normalized}")
        self._agents[normalized] = worker

    def get(self, name: str) -> AgentWorker:
        try:
            return self._agents[name]
        except KeyError as exc:
            raise KeyError(f"Unknown agent: {name}") from exc

    def names(self) -> tuple[str, ...]:
        return tuple(self._agents)

    def delegate(self, name: str, task_description: str, context: TaskContext) -> str:
        if not task_description.strip():
            raise ValueError("Task description must not be empty")
        return self.get(name)(task_description, context)
