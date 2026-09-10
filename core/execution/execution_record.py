from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4


@dataclass(frozen=True)
class ExecutionRecord:
    """Immutable audit record linking an action to its task and policy decision."""

    task_id: str
    command: str
    workspace: str
    return_code: int
    stdout: str
    stderr: str
    timed_out: bool
    policy_decision: str
    id: str = field(default_factory=lambda: uuid4().hex)
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def succeeded(self) -> bool:
        return self.return_code == 0 and not self.timed_out

    def __post_init__(self) -> None:
        if not self.task_id.strip():
            raise ValueError("Task ID must not be empty")
        if not self.command.strip():
            raise ValueError("Command must not be empty")
        if not self.workspace.strip():
            raise ValueError("Workspace must not be empty")
