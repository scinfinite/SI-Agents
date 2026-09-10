from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from uuid import uuid4


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    description: str
    id: str = field(default_factory=lambda: str(uuid4()))
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result: str | None = None
    error: str | None = None
    priority: int = 0
    dependencies: tuple[str, ...] = ()
    attempts: int = 0
    max_attempts: int = 1

    def __post_init__(self) -> None:
        if not self.description.strip():
            raise ValueError("Task description must not be empty")
        if self.priority < 0:
            raise ValueError("Task priority must not be negative")
        if self.max_attempts < 1:
            raise ValueError("Task max_attempts must be at least 1")
        if len(set(self.dependencies)) != len(self.dependencies):
            raise ValueError("Task dependencies must be unique")
        if self.id in self.dependencies:
            raise ValueError("Task cannot depend on itself")

    def start(self) -> None:
        if self.status is not TaskStatus.PENDING:
            raise ValueError(f"Cannot start task in state {self.status.value}")
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.now(UTC)
        self.attempts += 1

    def succeed(self, result: str) -> None:
        if self.status is not TaskStatus.RUNNING:
            raise ValueError(f"Cannot succeed task in state {self.status.value}")
        self.result = result
        self.error = None
        self.status = TaskStatus.SUCCEEDED
        self.completed_at = datetime.now(UTC)

    def fail(self, error: str) -> None:
        if self.status is not TaskStatus.RUNNING:
            raise ValueError(f"Cannot fail task in state {self.status.value}")
        if not error.strip():
            raise ValueError("Task failure must include an error")
        self.error = error
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.now(UTC)

    def cancel(self, reason: str = "") -> None:
        if self.status not in {TaskStatus.PENDING, TaskStatus.RUNNING}:
            raise ValueError(f"Cannot cancel task in state {self.status.value}")
        self.status = TaskStatus.CANCELLED
        self.error = reason or "Task cancelled"
        self.completed_at = datetime.now(UTC)

    @property
    def retryable(self) -> bool:
        return self.status is TaskStatus.FAILED and self.attempts < self.max_attempts
