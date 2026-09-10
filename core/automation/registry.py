"""In-memory automation registry with lifecycle and due-job queries."""

from datetime import datetime

from core.automation.models import AutomationJob, JobState


class AutomationRegistry:
    def __init__(self) -> None:
        self._jobs: dict[str, AutomationJob] = {}

    def register(self, job: AutomationJob) -> None:
        if job.job_id in self._jobs:
            raise ValueError(f"job already exists: {job.job_id}")
        self._jobs[job.job_id] = job

    def get(self, job_id: str) -> AutomationJob:
        try:
            return self._jobs[job_id]
        except KeyError as exc:
            raise KeyError(f"unknown automation job: {job_id}") from exc

    def list(self, *, state: JobState | None = None) -> tuple[AutomationJob, ...]:
        jobs = tuple(self._jobs.values())
        if state is not None:
            jobs = tuple(job for job in jobs if job.state == state)
        return jobs

    def due(self, now: datetime) -> tuple[AutomationJob, ...]:
        return tuple(
            job for job in self._jobs.values()
            if job.state == JobState.ENABLED and job.schedule.next_run_at <= now
        )

    def update(self, job: AutomationJob) -> None:
        if job.job_id not in self._jobs:
            raise KeyError(f"unknown automation job: {job.job_id}")
        self._jobs[job.job_id] = job

    def pause(self, job_id: str) -> AutomationJob:
        job = self.get(job_id)
        updated = AutomationJob(**{**job.__dict__, "state": JobState.PAUSED})
        self.update(updated)
        return updated

    def resume(self, job_id: str) -> AutomationJob:
        job = self.get(job_id)
        if job.state == JobState.CANCELLED:
            raise ValueError("cancelled jobs cannot be resumed")
        updated = AutomationJob(**{**job.__dict__, "state": JobState.ENABLED})
        self.update(updated)
        return updated

    def cancel(self, job_id: str) -> AutomationJob:
        job = self.get(job_id)
        updated = AutomationJob(**{**job.__dict__, "state": JobState.CANCELLED})
        self.update(updated)
        return updated
