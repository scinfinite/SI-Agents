import pytest

from core.state.checkpoints import CheckpointError, CheckpointStore


def test_create_and_get_checkpoint() -> None:
    store = CheckpointStore()

    checkpoint = store.create("task-1", "before modifying source")

    assert store.get(checkpoint.id) == checkpoint
    assert checkpoint.task_id == "task-1"
    assert checkpoint.description == "before modifying source"


def test_for_task_returns_only_matching_checkpoints() -> None:
    store = CheckpointStore()
    first = store.create("task-1", "first")
    second = store.create("task-2", "second")

    assert store.for_task("task-1") == (first,)
    assert store.for_task("task-2") == (second,)


def test_checkpoint_rejects_empty_values() -> None:
    store = CheckpointStore()

    with pytest.raises(ValueError, match="Task ID must not be empty"):
        store.create(" ", "checkpoint")

    with pytest.raises(ValueError, match="Checkpoint description must not be empty"):
        store.create("task-1", " ")


def test_unknown_checkpoint_is_an_error() -> None:
    with pytest.raises(CheckpointError, match="Unknown checkpoint"):
        CheckpointStore().get("missing")


def test_checkpoint_store_round_trips_metadata(tmp_path) -> None:
    path = tmp_path / "checkpoints.json"
    store = CheckpointStore(path)
    checkpoint = store.create("task-1", "before change", snapshot_id="snapshot-1")

    restored = CheckpointStore(path)
    assert restored.get(checkpoint.id) == checkpoint
