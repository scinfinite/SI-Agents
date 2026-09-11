from __future__ import annotations

import threading

import pytest

from core.runtime.execution import AuthorizedTask, ExecutionRuntime, ExecutionStore, RuntimeFailure, RuntimeErrorCode, State


class Adapter:
    def __init__(self, value="ok"):
        self.value = value
        self.cancelled = False

    def invoke(self, task, *, cancel):
        return self.value

    def cancel(self, task):
        self.cancelled = True


def test_lifecycle_reaches_single_terminal_state():
    store = ExecutionStore()
    runtime = ExecutionRuntime(store, Adapter())
    task = AuthorizedTask("task-1", "exec-1", {"x": 1})
    assert runtime.accept(task).state == State.QUEUED
    result = runtime.run("exec-1")
    assert result.state == State.SUCCEEDED
    assert runtime.run("exec-1").state == State.SUCCEEDED


def test_idempotency_reuses_attempt():
    store = ExecutionStore()
    runtime = ExecutionRuntime(store, Adapter())
    task = AuthorizedTask("task-1", "exec-1", {"x": 1})
    first = runtime.accept(task, idempotency_key="k")
    second = runtime.accept(task, idempotency_key="k")
    assert first.attempt_id == second.attempt_id


def test_idempotency_conflict_fails_closed():
    store = ExecutionStore()
    runtime = ExecutionRuntime(store, Adapter())
    runtime.accept(AuthorizedTask("task-1", "exec-1", {"x": 1}), idempotency_key="k")
    with pytest.raises(RuntimeFailure) as exc:
        runtime.accept(AuthorizedTask("task-2", "exec-2", {"x": 2}), idempotency_key="k")
    assert exc.value.code == RuntimeErrorCode.IDEMPOTENCY_CONFLICT


def test_cancel_is_terminal_and_calls_adapter():
    class BlockingAdapter(Adapter):
        def invoke(self, task, *, cancel):
            cancel.wait(1)
            return "late"

    adapter = BlockingAdapter()
    store = ExecutionStore()
    runtime = ExecutionRuntime(store, adapter)
    runtime.accept(AuthorizedTask("task-1", "exec-1", {}))
    thread = threading.Thread(target=runtime.run, args=("exec-1",))
    thread.start()
    runtime.cancel("exec-1")
    thread.join(timeout=2)
    assert store.get("exec-1").state == State.CANCELLED
    assert adapter.cancelled


def test_invalid_transition_is_rejected():
    store = ExecutionStore()
    runtime = ExecutionRuntime(store, Adapter())
    runtime.accept(AuthorizedTask("task-1", "exec-1", {}))
    with pytest.raises(RuntimeFailure) as exc:
        store.transition("exec-1", State.SUCCEEDED)
    assert exc.value.code == RuntimeErrorCode.INVALID_TRANSITION
