import pytest

from core.state.execution_state import ExecutionState, ExecutionStatus


def test_execution_state_tracks_lifecycle() -> None:
    state = ExecutionState(task_id="task-1")
    state.start()
    assert state.status is ExecutionStatus.RUNNING
    assert state.attempt == 1
    state.succeed()
    assert state.status is ExecutionStatus.SUCCEEDED
    assert state.completed_at is not None


def test_execution_failure_requires_reason() -> None:
    state = ExecutionState(task_id="task-1")
    state.start()
    with pytest.raises(ValueError, match="must include an error"):
        state.fail(" ")
    state.fail("command failed")
    assert state.status is ExecutionStatus.FAILED
    assert state.error == "command failed"


def test_terminal_execution_cannot_be_started_again() -> None:
    state = ExecutionState(task_id="task-1")
    state.start()
    state.cancel("operator cancelled")
    with pytest.raises(ValueError, match="Cannot start"):
        state.start()
