from datetime import UTC, datetime, timedelta

import pytest

from core.waiting import ScheduleSpec, WaitKind, WaitState, WaitingService


BASE = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)


def service(tmp_path):
    return WaitingService(tmp_path / ".si" / "waiting.v1.sqlite3")


def test_timer_is_durable_and_promotes_without_workers(tmp_path):
    db = service(tmp_path)
    wait = db.create(subject_id="u1", project_id="p1", kind=WaitKind.TIMER, wake_at=BASE + timedelta(minutes=5))
    assert wait.state is WaitState.WAITING
    assert db.promote_due(now=BASE + timedelta(minutes=4)) == 0
    assert db.promote_due(now=BASE + timedelta(minutes=5)) == 1
    assert db.get(wait.wait_id, subject_id="u1", project_id="p1").state is WaitState.READY


def test_restart_recovers_wait_and_events(tmp_path):
    path = tmp_path / ".si" / "waiting.v1.sqlite3"
    first = WaitingService(path)
    wait = first.create(subject_id="u1", project_id="p1", kind=WaitKind.EXTERNAL, wake_at=BASE, trigger="webhook")
    first.promote_due(now=BASE)
    second = WaitingService(path)
    restored = second.get(wait.wait_id, subject_id="u1", project_id="p1")
    assert restored.state is WaitState.READY
    assert [event["event"] for event in second.events(wait.wait_id, subject_id="u1", project_id="p1")] == ["created", "ready"]


def test_event_wake_and_deadline_fail_closed(tmp_path):
    db = service(tmp_path)
    wait = db.create(subject_id="u1", project_id="p1", kind=WaitKind.HUMAN, wake_at=BASE + timedelta(hours=1), deadline=BASE + timedelta(minutes=1))
    result = db.wake(wait.wait_id, subject_id="u1", project_id="p1", trigger="human-response", now=BASE + timedelta(minutes=1))
    assert result.state is WaitState.EXPIRED
    assert db.wake(wait.wait_id, subject_id="u1", project_id="p1", trigger="late") .state is WaitState.EXPIRED


def test_recurring_reschedules_and_bounds_occurrences(tmp_path):
    db = service(tmp_path)
    spec = ScheduleSpec(kind=WaitKind.RECURRING, interval_seconds=60, max_occurrences=2)
    wait = db.create(subject_id="u1", project_id="p1", kind=WaitKind.RECURRING, wake_at=BASE, schedule=spec)
    db.promote_due(now=BASE)
    claimed = db.claim_ready(subject_id="u1", project_id="p1", now=BASE)[0]
    next_wait = db.complete(claimed.wait_id, subject_id="u1", project_id="p1", expected_revision=claimed.revision, now=BASE)
    assert next_wait.state is WaitState.WAITING
    assert next_wait.occurrences == 1
    db.promote_due(now=BASE + timedelta(minutes=1))
    claimed = db.claim_ready(subject_id="u1", project_id="p1", now=BASE + timedelta(minutes=1))[0]
    terminal = db.complete(claimed.wait_id, subject_id="u1", project_id="p1", expected_revision=claimed.revision, now=BASE + timedelta(minutes=1))
    assert terminal.occurrences == 1


def test_priority_aging_prevents_old_low_priority_starvation(tmp_path):
    db = service(tmp_path)
    db.create(subject_id="u1", project_id="p1", kind=WaitKind.TIMER, wake_at=BASE, priority=-10, now=BASE - timedelta(hours=3))
    db.create(subject_id="u1", project_id="p1", kind=WaitKind.TIMER, wake_at=BASE, priority=10, now=BASE)
    db.promote_due(now=BASE)
    claimed = db.claim_ready(subject_id="u1", project_id="p1", now=BASE + timedelta(hours=3))[0]
    assert claimed.priority == -10


def test_cross_project_access_and_stale_revision_fail_closed(tmp_path):
    db = service(tmp_path)
    wait = db.create(subject_id="u1", project_id="p1", kind=WaitKind.TIMER, wake_at=BASE)
    with pytest.raises(KeyError):
        db.get(wait.wait_id, subject_id="u2", project_id="p1")
    db.promote_due(now=BASE)
    claimed = db.claim_ready(subject_id="u1", project_id="p1", now=BASE)[0]
    with pytest.raises(ValueError, match="stale"):
        db.complete(claimed.wait_id, subject_id="u1", project_id="p1", expected_revision=claimed.revision - 1)


def test_secret_and_oversized_payloads_rejected(tmp_path):
    db = service(tmp_path)
    with pytest.raises(ValueError, match="secret-like"):
        db.create(subject_id="u1", project_id="p1", kind=WaitKind.TIMER, wake_at=BASE, payload={"api_key": "no"})
    with pytest.raises(ValueError, match="16 KiB"):
        db.create(subject_id="u1", project_id="p1", kind=WaitKind.TIMER, wake_at=BASE, payload={"data": "x" * 20_000})


def test_cron_and_validation(tmp_path):
    db = service(tmp_path)
    spec = ScheduleSpec(kind=WaitKind.CRON, cron="*/5 * * * *", max_occurrences=3)
    wait = db.create(subject_id="u1", project_id="p1", kind=WaitKind.CRON, wake_at=BASE.replace(minute=5), schedule=spec)
    db.promote_due(now=BASE.replace(minute=5))
    claimed = db.claim_ready(subject_id="u1", project_id="p1", now=BASE.replace(minute=5))[0]
    next_wait = db.complete(claimed.wait_id, subject_id="u1", project_id="p1", expected_revision=claimed.revision, now=BASE.replace(minute=5))
    assert next_wait.wake_at.minute == 10
    with pytest.raises(ValueError):
        ScheduleSpec(kind=WaitKind.CRON, cron="bad cron")


def test_cancel_is_idempotent_and_payload_is_json_safe(tmp_path):
    db = service(tmp_path)
    wait = db.create(subject_id="u1", project_id="p1", kind=WaitKind.RESOURCE, wake_at=BASE, payload={"usage": {"cpu": 2}})
    cancelled = db.cancel(wait.wait_id, subject_id="u1", project_id="p1", reason="released", now=BASE)
    assert cancelled.state is WaitState.CANCELLED
    assert db.cancel(wait.wait_id, subject_id="u1", project_id="p1").state is WaitState.CANCELLED
