from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Protocol
from uuid import uuid4


@dataclass(frozen=True)
class AgentSpec:
    name: str
    responsibility: str
    deliverables: tuple[str, ...]
    success_criteria: tuple[str, ...]
    boundaries: tuple[str, ...]
    required_permissions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.responsibility.strip():
            raise ValueError("Agent identity and responsibility are required")
        if not self.deliverables or not self.success_criteria:
            raise ValueError("Agent must declare deliverables and success criteria")


@dataclass
class AgentContext:
    task_id: str
    values: dict[str, Any] = field(default_factory=dict)

    def require(self, key: str) -> Any:
        if key not in self.values:
            raise KeyError(f"Missing agent context value: {key}")
        return self.values[key]


@dataclass(frozen=True)
class AgentResult:
    agent: str
    status: str
    summary: str
    evidence_ids: tuple[str, ...] = ()
    handoff: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: uuid4().hex)
    completed_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class AgentWorker(Protocol):
    def __call__(self, context: AgentContext) -> AgentResult: ...
