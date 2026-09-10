from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from threading import Lock
from typing import Any
from uuid import uuid4


class ContextMode(StrEnum):
    SHARED = "shared"
    ISOLATED = "isolated"


class TaskStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"
    ESCALATED = "escalated"

    @property
    def terminal(self) -> bool:
        return self in {
            TaskStatus.SUCCEEDED,
            TaskStatus.FAILED,
            TaskStatus.SKIPPED,
            TaskStatus.CANCELLED,
            TaskStatus.ESCALATED,
        }


class WorkflowEventType(StrEnum):
    WORKFLOW_STARTED = "workflow_started"
    TASK_READY = "task_ready"
    TASK_STARTED = "task_started"
    TASK_RETRY = "task_retry"
    TASK_SUCCEEDED = "task_succeeded"
    TASK_FAILED = "task_failed"
    TASK_ESCALATED = "task_escalated"
    TASK_SKIPPED = "task_skipped"
    CHECKPOINT = "checkpoint"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    WORKFLOW_CANCELLED = "workflow_cancelled"


@dataclass(frozen=True)
class TaskDefinition:
    id: str
    agent_id: str
    depends_on: tuple[str, ...] = ()
    context_mode: ContextMode = ContextMode.ISOLATED
    max_attempts: int = 1
    requires_evidence: bool = False
    verification_gate: bool = False
    escalate_to: str | None = None
    metadata: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        _require_id(self.id, "task id")
        _require_id(self.agent_id, "agent id")
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if self.id in self.depends_on:
            raise ValueError(f"task {self.id} cannot depend on itself")
        if len(set(self.depends_on)) != len(self.depends_on):
            raise ValueError(f"task {self.id} has duplicate dependencies")
        if self.escalate_to is not None:
            _require_id(self.escalate_to, "escalation agent id")
        if len({key for key, _ in self.metadata}) != len(self.metadata):
            raise ValueError(f"task {self.id} has duplicate metadata keys")


@dataclass(frozen=True)
class TeamDefinition:
    id: str
    name: str
    description: str
    members: tuple[str, ...]
    tasks: tuple[TaskDefinition, ...]
    max_parallelism: int = 1
    required_evidence: bool = True

    def __post_init__(self) -> None:
        _require_id(self.id, "team id")
        if not self.name.strip() or not self.description.strip():
            raise ValueError("team name and description are required")
        if not self.members:
            raise ValueError("team must declare at least one member")
        if len(set(self.members)) != len(self.members):
            raise ValueError("team members must be unique")
        if not self.tasks:
            raise ValueError("team must declare at least one task")
        if self.max_parallelism < 1:
            raise ValueError("max_parallelism must be at least 1")
        task_ids = {task.id for task in self.tasks}
        if len(task_ids) != len(self.tasks):
            raise ValueError("team task ids must be unique")
        missing_dependencies = {
            dependency
            for task in self.tasks
            for dependency in task.depends_on
            if dependency not in task_ids
        }
        if missing_dependencies:
            raise ValueError(f"unknown task dependencies: {sorted(missing_dependencies)}")
        non_members = {task.agent_id for task in self.tasks if task.agent_id not in set(self.members)}
        if non_members:
            raise ValueError(f"tasks reference agents outside team: {sorted(non_members)}")


@dataclass(frozen=True)
class WorkflowEvent:
    type: WorkflowEventType
    execution_id: str
    sequence: int
    task_id: str | None = None
    data: object = None
    emitted_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.execution_id.strip() or self.sequence < 0:
            raise ValueError("workflow event requires execution id and non-negative sequence")
        if self.emitted_at.tzinfo is None:
            raise ValueError("workflow event timestamp must be timezone-aware")


@dataclass
class TeamExecution:
    team_id: str
    execution_id: str = field(default_factory=lambda: str(uuid4()))
    status: TaskStatus = TaskStatus.PENDING
    task_status: dict[str, TaskStatus] = field(default_factory=dict)
    attempts: dict[str, int] = field(default_factory=dict)
    results: dict[str, Any] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)
    events: list[WorkflowEvent] = field(default_factory=list)
    checkpoints: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    _event_lock: Lock = field(default_factory=Lock, init=False, repr=False)

    def emit(
        self,
        event_type: WorkflowEventType,
        *,
        task_id: str | None = None,
        data: object = None,
    ) -> None:
        with self._event_lock:
            self.events.append(
                WorkflowEvent(
                    event_type,
                    self.execution_id,
                    len(self.events),
                    task_id=task_id,
                    data=data,
                )
            )


def _require_id(value: str, label: str) -> None:
    if not value or value != value.strip() or any(
        char not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for char in value
    ):
        raise ValueError(f"Invalid {label}: {value!r}")
