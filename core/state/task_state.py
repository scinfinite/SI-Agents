from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from uuid import uuid4


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass
class Task:
    description: str
    id: str = field(default_factory=lambda: str(uuid4()))
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    result: str | None = None
    error: str | None = None

    def start(self) -> None:
        if self.status is not TaskStatus.PENDING:
            raise ValueError(f"Cannot start task in state {self.status.value}")
        self.status = TaskStatus.RUNNING

    def succeed(self, result: str) -> None:
        if self.status is not TaskStatus.RUNNING:
            raise ValueError(f"Cannot succeed task in state {self.status.value}")
        self.result = result
        self.status = TaskStatus.SUCCEEDED

    def fail(self, error: str) -> None:
        if self.status is not TaskStatus.RUNNING:
            raise ValueError(f"Cannot fail task in state {self.status.value}")
        self.error = error
        self.status = TaskStatus.FAILED
