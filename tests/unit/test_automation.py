"""Acceptance and adversarial tests for Phase 15 automation."""

from datetime import UTC, datetime, timedelta

import pytest

from core.automation import (
    AutomationJob,
    AutomationRegistry,
    AutomationRunner,
    AutomationScheduler,
    AutomationStore,
    JobState,
    RetryPolicy,
    RunStatus,
    Schedule,
    ScheduleKind,
)
from core.governance.models import Approval, DataClass, GovernanceRequest, RiskLevel

NOW = datetime(2026, 9, 10, 10, 0, tzinfo=UTC)


def job(**kwargs: object) -> AutomationJob:
    return AutomationJob(
        job_id=kwargs.pop("job_id", "job-1"),
        name="test",
        action="work",
        schedule=kwargs.pop("schedule", Schedule(ScheduleKind.ONCE, NOW)),
        **kwargs,
    )


def test_registry_rejects_duplicates_and_lifecycle_is_explicit() -> None:
    registry = AutomationRegistry()
    registry.register(job())
    with pytest.raises(ValueError):
        registry.register(job())
    assert registry.pause("job-1").state == JobState.PAUSED
    assert registry.resume("job-1").state == JobState.ENABLED
    assert registry.cancel("job-1").state == JobState.CANCELLED
    with pytest.raises(ValueError):
        registry.resume("job-1")


def test_scheduler_orders_due_jobs_and_one_shot_is_cancelled() -> None:
    registry = AutomationRegistry()
    registry.register(job(job_id="b", schedule=Schedule(ScheduleKind.ONCE, NOW)))
    registry.register(job(job_id="a", schedule=Schedule(ScheduleKind.ONCE, NOW - timedelta(seconds=1))))
    scheduler = AutomationScheduler(registry)
    assert [item.job_id for item in scheduler.due(NOW)] == ["a", "b"]
    assert scheduler.mark_triggered(registry.get("b"), NOW).state == JobState.CANCELLED


def test_interval_schedule_catches_up_without_drift() -> None:
    schedule = Schedule(ScheduleKind.INTERVAL, NOW - timedelta(seconds=25), 10)
    advanced = schedule.advance(NOW)
    assert advanced is not None
    assert advanced.next_run_at == NOW + timedelta(seconds=5)


def test_invalid_schedule_and_retry_values_fail_closed() -> None:
    with pytest.raises(ValueError):
        Schedule(ScheduleKind.INTERVAL, NOW)
    with pytest.raises(ValueError):
        RetryPolicy(max_attempts=0)
    with pytest.raises(ValueError):
        RetryPolicy(backoff_seconds=5, max_backoff_seconds=1)


def test_runner_retries_with_exponential_backoff_and_records_failure() -> None:
    calls: list[int] = []
    delays: list[float] = []

    def action(_: dict[str, object]) -> None:
        calls.append(1)
        raise RuntimeError("boom")

    runner = AutomationRunner({"work": action}, sleeper=delays.append)
    record = runner.execute(job(retry=RetryPolicy(max_attempts=3, backoff_seconds=2, max_backoff_seconds=10)))
    assert record.status == RunStatus.FAILED
    assert record.attempts == 3
    assert calls == [1, 1, 1]
    assert delays == [2, 4]


def test_runner_idempotency_prevents_duplicate_success() -> None:
    calls: list[int] = []
    runner = AutomationRunner({"work": lambda _: calls.append(1)})
    target = job(idempotency_key="stable-key")
    assert runner.execute(target).status == RunStatus.SUCCESS
    assert runner.execute(target).status == RunStatus.SKIPPED
    assert calls == [1]


def test_runner_precondition_skips_without_execution() -> None:
    calls: list[int] = []
    runner = AutomationRunner({"work": lambda _: calls.append(1)})
    record = runner.execute(job(), condition=lambda _: False)
    assert record.status == RunStatus.SKIPPED
    assert calls == []


def test_paid_automation_requires_approval() -> None:
    calls: list[int] = []
    runner = AutomationRunner({"work": lambda _: calls.append(1)})
    request = GovernanceRequest(action="work", risk=RiskLevel.LOW, paid_resource=True)
    blocked = runner.execute(job(), governance_request=request)
    assert blocked.status == RunStatus.APPROVAL_REQUIRED
    assert calls == []
    approved = GovernanceRequest(
        action="work", risk=RiskLevel.LOW, paid_resource=True,
        approval=Approval("human", "approved for this run"),
    )
    assert runner.execute(job(job_id="job-2"), governance_request=approved).status == RunStatus.SUCCESS
    assert calls == [1]


def test_sensitive_egress_requires_governance_approval() -> None:
    runner = AutomationRunner({"work": lambda _: pytest.fail("must not execute")})
    request = GovernanceRequest(
        action="work", risk=RiskLevel.MEDIUM, data_class=DataClass.SENSITIVE, external_egress=True,
    )
    record = runner.execute(job(), governance_request=request)
    assert record.status == RunStatus.APPROVAL_REQUIRED


def test_json_store_round_trip_preserves_jobs_and_runs(tmp_path: object) -> None:
    path = tmp_path / "automation.json"
    registry = AutomationRegistry()
    target = job(
        schedule=Schedule(ScheduleKind.INTERVAL, NOW, 60),
        retry=RetryPolicy(max_attempts=2, backoff_seconds=1),
        tags=("maintenance", "verification"),
    )
    registry.register(target)
    runner = AutomationRunner({"work": lambda _: None})
    runner.execute(target)
    store = AutomationStore()
    store.save(path, registry, runner.history)
    restored, runs = store.load(path)
    assert restored.get("job-1") == target
    assert runs[0].status == RunStatus.SUCCESS


def test_store_rejects_malformed_root(tmp_path: object) -> None:
    path = tmp_path / "bad.json"
    path.write_text("[]", encoding="utf-8")
    with pytest.raises(TypeError):
        AutomationStore().load(path)
