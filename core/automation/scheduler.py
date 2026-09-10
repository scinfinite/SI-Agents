"""Deterministic scheduler: selects due work but never executes it."""

from datetime import datetime

from core.automation.models import AutomationJob, JobState
from core.automation.registry import AutomationRegistry


class AutomationScheduler:
    def __init__(self, registry: AutomationRegistry) -> None:
        self.registry = registry

    def due(self, now: datetime) -> tuple[AutomationJob, ...]:
        return tuple(sorted(self.registry.due(now), key=lambda job: (job.schedule.next_run_at, job.job_id)))

    def mark_triggered(self, job: AutomationJob, now: datetime) -> AutomationJob:
        next_schedule = job.schedule.advance(now)
        if next_schedule is None:
            updated = AutomationJob(**{**job.__dict__, "schedule": job.schedule, "state": JobState.CANCELLED})
        else:
            updated = AutomationJob(**{**job.__dict__, "schedule": next_schedule})
        self.registry.update(updated)
        return updated
