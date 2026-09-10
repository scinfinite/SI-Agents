"""Automation domain models with deterministic scheduling semantics."""

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum


class ScheduleKind(str, Enum):
    ONCE = "once"
    INTERVAL = "interval"


class JobState(str, Enum):
    ENABLED = "enabled"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class RunStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    APPROVAL_REQUIRED = "approval_required"


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 1
    backoff_seconds: float = 0.0
    max_backoff_seconds: float = 3600.0

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if self.backoff_seconds < 0 or self.max_backoff_seconds < 0:
            raise ValueError("backoff values must be non-negative")
        if self.backoff_seconds > self.max_backoff_seconds:
            raise ValueError("backoff_seconds must not exceed max_backoff_seconds")

    def delay_for(self, attempt: int) -> float:
        if attempt < 1:
            raise ValueError("attempt must be positive")
        return min(self.backoff_seconds * (2 ** (attempt - 1)), self.max_backoff_seconds)


@dataclass(frozen=True)
class Schedule:
    kind: ScheduleKind
    next_run_at: datetime
    interval_seconds: float | None = None

    def __post_init__(self) -> None:
        if self.next_run_at.tzinfo is None:
            raise ValueError("next_run_at must be timezone-aware")
        if self.kind == ScheduleKind.INTERVAL and (self.interval_seconds is None or self.interval_seconds <= 0):
            raise ValueError("interval schedules require a positive interval_seconds")
        if self.kind == ScheduleKind.ONCE and self.interval_seconds is not None:
            raise ValueError("once schedules cannot define interval_seconds")

    def advance(self, now: datetime) -> "Schedule | None":
        if self.kind == ScheduleKind.ONCE:
            return None
        assert self.interval_seconds is not None
        next_run = self.next_run_at
        while next_run <= now:
            next_run += timedelta(seconds=self.interval_seconds)
        return Schedule(ScheduleKind.INTERVAL, next_run, self.interval_seconds)


@dataclass(frozen=True)
class AutomationJob:
    job_id: str
    name: str
    action: str
    payload: dict[str, object] = field(default_factory=dict)
    schedule: Schedule = field(default_factory=lambda: Schedule(ScheduleKind.ONCE, datetime.now(UTC)))
    retry: RetryPolicy = field(default_factory=RetryPolicy)
    state: JobState = JobState.ENABLED
    idempotency_key: str | None = None
    tags: tuple[str, ...] = ()
    governance_action: str | None = None

    def __post_init__(self) -> None:
        if not self.job_id.strip() or not self.name.strip() or not self.action.strip():
            raise ValueError("job_id, name, and action must not be empty")
        if self.idempotency_key is not None and not self.idempotency_key.strip():
            raise ValueError("idempotency_key must not be blank")


@dataclass(frozen=True)
class RunRecord:
    run_id: str
    job_id: str
    status: RunStatus
    started_at: datetime
    finished_at: datetime
    attempts: int
    message: str
    idempotency_key: str | None = None
    decision_status: str | None = None

    def __post_init__(self) -> None:
        if self.finished_at < self.started_at or self.attempts < 0:
            raise ValueError("invalid run timing or attempts")
