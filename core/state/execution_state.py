from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from uuid import uuid4


class ExecutionStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ExecutionState:
    task_id: str
    status: ExecutionStatus = ExecutionStatus.CREATED
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    completed_at: datetime | None = None
    attempt: int = 0
    error: str | None = None

    def start(self) -> None:
        if self.status is not ExecutionStatus.CREATED:
            raise ValueError(f"Cannot start execution in state {self.status.value}")
        self.status = ExecutionStatus.RUNNING
        self.started_at = datetime.now(UTC)
        self.attempt += 1

    def succeed(self) -> None:
        if self.status is not ExecutionStatus.RUNNING:
            raise ValueError(f"Cannot succeed execution in state {self.status.value}")
        self.status = ExecutionStatus.SUCCEEDED
        self.completed_at = datetime.now(UTC)

    def fail(self, error: str) -> None:
        if self.status is not ExecutionStatus.RUNNING:
            raise ValueError(f"Cannot fail execution in state {self.status.value}")
        if not error.strip():
            raise ValueError("Execution failure must include an error")
        self.status = ExecutionStatus.FAILED
        self.error = error
        self.completed_at = datetime.now(UTC)

    def cancel(self, reason: str = "") -> None:
        if self.status not in {ExecutionStatus.CREATED, ExecutionStatus.RUNNING}:
            raise ValueError(f"Cannot cancel execution in state {self.status.value}")
        self.status = ExecutionStatus.CANCELLED
        self.error = reason or "Execution cancelled"
        self.completed_at = datetime.now(UTC)
