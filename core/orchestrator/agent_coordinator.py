class AgentCoordinator:
    """Coordinate named agent workers without granting them implicit permissions."""

    def __init__(self) -> None:
        self._agents: dict[str, object] = {}

    def register(self, name: str, worker: object) -> None:
        normalized = name.strip()
        if not normalized:
            raise ValueError("Agent name must not be empty")
        if not callable(worker):
            raise TypeError("Agent worker must be callable")
        if normalized in self._agents:
            raise ValueError(f"Agent already registered: {normalized}")
        self._agents[normalized] = worker

    def get(self, name: str) -> object:
        try:
            return self._agents[name]
        except KeyError as exc:
            raise KeyError(f"Unknown agent: {name}") from exc

    def names(self) -> tuple[str, ...]:
        return tuple(self._agents)

    def delegate(self, name: str, task_description: str, context: object) -> str:
        if not task_description.strip():
            raise ValueError("Task description must not be empty")
        worker = self.get(name)
        if not callable(worker):
            raise TypeError(f"Registered agent is not callable: {name}")
        result = worker(task_description, context)
        if not isinstance(result, str):
            raise TypeError("Agent worker must return a string")
        return result
