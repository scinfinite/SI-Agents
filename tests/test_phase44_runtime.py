from __future__ import annotations

import threading
import time

import pytest

from core.runtime.execution import (
    AuthorizedTask,
    ExecutionRuntime,
    ExecutionStore,
    RuntimeErrorCode,
    RuntimeFailure,
    State,
)


class Adapter:
    def __init__(self, value=None, fail=False):
        self.value = value or {"ok": True}
        self.fail = fail
        self.cancelled = False
        self.paused = False
        self.resumed = False

    def invoke(self, task, cancel_event):
        if self.fail:
            raise ValueError("adapter boom")
        return self.value

    def cancel(self, execution_id):
        self.cancelled = True

    def pause(self, execution_id):
        self.paused = True

    def resume(self, execution_id):
        self.resumed = True


def test_lifecycle_and_terminal_idempotence():
    store = ExecutionStore()
    runtime = ExecutionRuntime(store)
    execution = runtime.accept(AuthorizedTask("task-1", {"x": 1}, execution_id="exec-1"))
    assert execution.state == State.QUEUED
    assert runtime.run("exec-1", Adapter()).state == State.SUCCEEDED
    assert runtime.run("exec-1", Adapter()).state == State.SUCCEEDED


def test_idempotency_reuses_execution_and_attempt():
    store = ExecutionStore()
    runtime = ExecutionRuntime(store)
    task = AuthorizedTask("task-1", {"x": 1}, idempotency_key="k")
    first = runtime.accept(task)
    second = runtime.accept(task)
    assert first.execution_id == second.execution_id
    assert first.attempt_id == second.attempt_id


def test_idempotency_conflict_fails_closed():
    store = ExecutionStore()
    runtime = ExecutionRuntime(store)
    runtime.accept(AuthorizedTask("task-1", {"x": 1}, idempotency_key="k"))
    with pytest.raises(RuntimeFailure) as exc:
        runtime.accept(AuthorizedTask("task-1", {"x": 2}, idempotency_key="k"))
    assert exc.value.code == RuntimeErrorCode.IDEMPOTENCY_CONFLICT


def test_adapter_failure_is_normalized_and_retry_creates_new_attempt():
    store = ExecutionStore()
    runtime = ExecutionRuntime(store)
    runtime.accept(AuthorizedTask("task-1", {}, execution_id="exec-1"))
    failed = runtime.run("exec-1", Adapter(fail=True))
    assert failed.state == State.FAILED
    assert failed.error_code == RuntimeErrorCode.ADAPTER_FAILURE.value
    retry = runtime.retry("exec-1")
    assert retry.number == 2
    assert retry.attempt_id != failed.attempt_id
    assert store.get("exec-1").state == State.QUEUED


def test_cancel_is_terminal_and_calls_adapter():
    class BlockingAdapter(Adapter):
        def invoke(self, task, cancel_event):
            cancel_event.wait(1)
            return {"late": True}

    adapter = BlockingAdapter()
    store = ExecutionStore()
    runtime = ExecutionRuntime(store)
    runtime.accept(AuthorizedTask("task-1", {}, execution_id="exec-1"))
    thread = threading.Thread(target=runtime.run, args=("exec-1", adapter))
    thread.start()
    time.sleep(0.05)
    runtime.cancel("exec-1")
    thread.join(timeout=2)
    assert store.get("exec-1").state == State.CANCELLED
    assert adapter.cancelled


def test_deadline_expires_before_adapter_invocation():
    store = ExecutionStore()
    runtime = ExecutionRuntime(store)
    runtime.accept(AuthorizedTask("task-1", {}, execution_id="exec-1", deadline_at=time.time() - 1))
    result = runtime.run("exec-1", Adapter())
    assert result.state == State.EXPIRED
    assert result.error_code == RuntimeErrorCode.DEADLINE_EXCEEDED.value


def test_pause_resume_are_adapter_capability_gated():
    store = ExecutionStore()
    runtime = ExecutionRuntime(store)
    adapter = Adapter()
    runtime.accept(AuthorizedTask("task-1", {}, execution_id="exec-1"))
    assert runtime.pause("exec-1", adapter).pause_requested
    assert runtime.resume("exec-1", adapter).pause_requested is False
    assert adapter.resumed


def test_restart_recovery_requeues_running_work():
    store = ExecutionStore()
    runtime = ExecutionRuntime(store)
    runtime.accept(AuthorizedTask("task-1", {}, execution_id="exec-1"))
    store.transition("exec-1", State.RUNNING)
    recovered = store.recover()
    assert recovered[0].state == State.QUEUED
    assert store.get("exec-1").attempt_number == 1


def test_persistence_survives_store_reopen(tmp_path):
    db = tmp_path / "runtime.sqlite"
    first = ExecutionStore(db)
    runtime = ExecutionRuntime(first)
    execution = runtime.accept(AuthorizedTask("task-1", {"x": 1}, execution_id="exec-1"))
    first.close()
    second = ExecutionStore(db)
    assert second.get(execution.execution_id).state == State.QUEUED
    second.close()


def test_invalid_transition_is_rejected():
    store = ExecutionStore()
    runtime = ExecutionRuntime(store)
    runtime.accept(AuthorizedTask("task-1", {}, execution_id="exec-1"))
    with pytest.raises(RuntimeFailure) as exc:
        store.transition("exec-1", State.SUCCEEDED)
    assert exc.value.code == RuntimeErrorCode.INVALID_TRANSITION


def test_inline_secret_like_fields_are_rejected():
    store = ExecutionStore()
    with pytest.raises(RuntimeFailure) as exc:
        store.create(AuthorizedTask("task-1", {"api_key": "do-not-store"}))
    assert exc.value.code == RuntimeErrorCode.SECRET_LEAK
