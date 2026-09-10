from core.state.execution_state import ExecutionState, ExecutionStatus
from core.state.execution_state_store import ExecutionStateStore


def test_execution_state_store_round_trips(tmp_path) -> None:
    path = tmp_path / "executions.json"
    store = ExecutionStateStore(path)
    state = ExecutionState(task_id="task-1")
    store.record(state)
    state.start()
    state.succeed()
    store.update(state)

    restored = ExecutionStateStore(path)
    loaded = restored.get(state.id)
    assert loaded.task_id == "task-1"
    assert loaded.status is ExecutionStatus.SUCCEEDED
    assert loaded.attempt == 1


def test_execution_state_store_rejects_unknown_update() -> None:
    store = ExecutionStateStore()
    state = ExecutionState(task_id="task-1")
    try:
        store.update(state)
    except KeyError as exc:
        assert "Unknown execution state" in str(exc)
    else:
        raise AssertionError("Unknown execution state should be rejected")
