from __future__ import annotations

import sqlite3

import pytest

from core.runtime import AuthorizedTask, CheckpointError, CheckpointStore, ExecutionStore, State


def _execution(store: ExecutionStore, *, task_id: str = "task"):
    return store.create(AuthorizedTask(task_id=task_id, payload={"step": 1}))


def test_checkpoint_is_durable_ordered_and_hash_verified(tmp_path):
    execution_store = ExecutionStore(tmp_path / "execution.db")
    checkpoint_store = CheckpointStore(tmp_path / "checkpoint.db")
    execution = _execution(execution_store)
    first = checkpoint_store.save(execution, {"cursor": 1})
    second = checkpoint_store.save(execution, {"cursor": 2}, parent_checkpoint_id=first.checkpoint_id)

    assert checkpoint_store.latest(execution.execution_id) == second
    assert checkpoint_store.verify_lineage(execution.execution_id) == (first, second)
    assert checkpoint_store.get(first.checkpoint_id).digest == first.digest

    checkpoint_store.close()
    reopened = CheckpointStore(tmp_path / "checkpoint.db")
    assert reopened.latest(execution.execution_id).checkpoint_id == second.checkpoint_id


def test_checkpoint_digest_detects_tampering(tmp_path):
    execution_store = ExecutionStore(tmp_path / "execution.db")
    checkpoint_store = CheckpointStore(tmp_path / "checkpoint.db")
    execution = _execution(execution_store)
    checkpoint = checkpoint_store.save(execution, {"cursor": 7})
    checkpoint_store._db.execute("UPDATE checkpoints SET state=? WHERE checkpoint_id=?", ('{"cursor":99}', checkpoint.checkpoint_id))

    with pytest.raises(CheckpointError, match="integrity"):
        checkpoint_store.verify(checkpoint.checkpoint_id)


def test_checkpoint_rejects_secret_material_and_oversized_state(tmp_path):
    execution_store = ExecutionStore(tmp_path / "execution.db")
    checkpoint_store = CheckpointStore(tmp_path / "checkpoint.db")
    execution = _execution(execution_store)

    with pytest.raises(CheckpointError, match="secret-like"):
        checkpoint_store.save(execution, {"api_key": "do-not-store"})
    with pytest.raises(CheckpointError, match="maximum"):
        checkpoint_store.save(execution, {"data": "x" * 300_000})


def test_checkpoint_parent_must_be_same_execution(tmp_path):
    execution_store = ExecutionStore(tmp_path / "execution.db")
    checkpoint_store = CheckpointStore(tmp_path / "checkpoint.db")
    first = _execution(execution_store, task_id="one")
    second = _execution(execution_store, task_id="two")
    parent = checkpoint_store.save(first, {"cursor": 1})

    with pytest.raises(CheckpointError, match="outside"):
        checkpoint_store.save(second, {"cursor": 2}, parent_checkpoint_id=parent.checkpoint_id)


def test_resume_creates_new_attempt_from_verified_checkpoint(tmp_path):
    execution_store = ExecutionStore(tmp_path / "execution.db")
    checkpoint_store = CheckpointStore(tmp_path / "checkpoint.db")
    execution = _execution(execution_store)
    checkpoint = checkpoint_store.save(execution, {"cursor": 4, "completed": ["a", "b"]})
    execution_store.transition(execution.execution_id, State.QUEUED)
    execution_store.transition(execution.execution_id, State.RUNNING)
    execution_store.transition(execution.execution_id, State.FAILED, error_code="adapter_failure")

    plan = checkpoint_store.resume(checkpoint.checkpoint_id, execution_store)
    resumed = execution_store.get(execution.execution_id)

    assert plan.checkpoint_id == checkpoint.checkpoint_id
    assert plan.state["cursor"] == 4
    assert plan.attempt_number == 2
    assert plan.attempt_id == resumed.attempt_id
    assert resumed.state == State.QUEUED


def test_resume_rejects_active_execution_and_missing_checkpoint(tmp_path):
    execution_store = ExecutionStore(tmp_path / "execution.db")
    checkpoint_store = CheckpointStore(tmp_path / "checkpoint.db")
    execution = _execution(execution_store)
    checkpoint = checkpoint_store.save(execution, {"cursor": 1})
    execution_store.transition(execution.execution_id, State.QUEUED)

    with pytest.raises(CheckpointError, match="terminal"):
        checkpoint_store.resume(checkpoint.checkpoint_id, execution_store)
    with pytest.raises(CheckpointError, match="not found"):
        checkpoint_store.verify("missing")


def test_resume_preserves_lineage_metadata_without_restoring_authority(tmp_path):
    execution_store = ExecutionStore(tmp_path / "execution.db")
    checkpoint_store = CheckpointStore(tmp_path / "checkpoint.db")
    execution = _execution(execution_store)
    checkpoint = checkpoint_store.save(execution, {"cursor": 1}, metadata={"provider": "safe-ref"})
    execution_store.transition(execution.execution_id, State.QUEUED)
    execution_store.transition(execution.execution_id, State.RUNNING)
    execution_store.transition(execution.execution_id, State.CANCELLED, error_code="cancelled")

    plan = checkpoint_store.resume(checkpoint.checkpoint_id, execution_store)
    assert plan.parent_checkpoint_id is None
    assert "provider" not in plan.state
    assert plan.state == {"cursor": 1}


def test_checkpoint_schema_survives_sqlite_reopen(tmp_path):
    execution_store = ExecutionStore(tmp_path / "execution.db")
    checkpoint_store = CheckpointStore(tmp_path / "checkpoint.db")
    execution = _execution(execution_store)
    checkpoint_store.save(execution, {"cursor": 9})
    checkpoint_store.close()

    db = sqlite3.connect(tmp_path / "checkpoint.db")
    assert db.execute("SELECT COUNT(*) FROM checkpoints").fetchone()[0] == 1
    db.close()
