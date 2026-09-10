from core.orchestrator.task_manager import TaskManager
from core.state.task_state import TaskStatus


def test_ready_tasks_are_dependency_aware_and_priority_ordered() -> None:
    manager = TaskManager()
    first = manager.create("first")
    second = manager.create("second", priority=10)
    dependent = manager.create("dependent", dependencies=(first.id,))

    assert [task.id for task in manager.ready()] == [second.id, first.id]

    first.start()
    first.succeed("ok")
    manager.persist()

    assert [task.id for task in manager.ready()] == [second.id, dependent.id]


def test_retry_resets_failed_task_to_pending() -> None:
    manager = TaskManager()
    task = manager.create("retry me", max_attempts=2)
    task.start()
    task.fail("temporary failure")

    assert task.retryable
    manager.retry(task.id)
    assert task.status is TaskStatus.PENDING
    assert task.error is None


def test_persistent_manager_round_trips_tasks(tmp_path) -> None:
    state_path = tmp_path / "tasks.json"
    manager = TaskManager(state_path)
    task = manager.create("persist me", priority=3, max_attempts=2)
    task.start()
    task.succeed("result")
    manager.persist()

    restored = TaskManager(state_path)
    loaded = restored.get(task.id)
    assert loaded.description == "persist me"
    assert loaded.priority == 3
    assert loaded.status is TaskStatus.SUCCEEDED
    assert loaded.result == "result"
    assert loaded.attempts == 1


def test_unknown_dependency_is_rejected() -> None:
    manager = TaskManager()
    try:
        manager.create("invalid", dependencies=("missing",))
    except KeyError as exc:
        assert "Unknown task dependency" in str(exc)
    else:
        raise AssertionError("Unknown dependency should be rejected")
