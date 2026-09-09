import pytest

from core.orchestrator.orchestrator import Orchestrator
from core.orchestrator.task_manager import TaskManager
from core.state.checkpoints import CheckpointStore
from core.state.task_state import TaskStatus


def test_run_executes_worker_and_returns_result() -> None:
    manager = TaskManager()
    orchestrator = Orchestrator(manager)

    result = orchestrator.run("inspect repository", lambda task: f"done: {task}")

    assert result == "done: inspect repository"


def test_task_manager_rejects_empty_description() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        TaskManager().create("   ")


def test_failed_worker_marks_task_failed() -> None:
    manager = TaskManager()
    orchestrator = Orchestrator(manager)

    def worker(_: str) -> str:
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        orchestrator.run("broken task", worker)

    task = manager.all()[0]
    assert task.status is TaskStatus.FAILED
    assert task.error == "boom"


def test_checkpoint_requires_known_task() -> None:
    orchestrator = Orchestrator(TaskManager(), CheckpointStore())

    with pytest.raises(KeyError, match="Unknown task"):
        orchestrator.checkpoint("missing", "before modification")


def test_checkpoint_records_known_task() -> None:
    orchestrator = Orchestrator(TaskManager(), CheckpointStore())
    task = orchestrator.tasks.create("modify project")

    checkpoint = orchestrator.checkpoint(task.id, "before modification")

    assert checkpoint.task_id == task.id
    assert orchestrator.checkpoints.for_task(task.id) == (checkpoint,)
