"""Durable, integrity-checked checkpoints and resume plans for V4 execution."""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from core.runtime.events import EventBus
from core.runtime.execution import Execution, ExecutionStore, State

_SECRET_KEY = re.compile(
    r"(?:password|passwd|secret|token|api[_-]?key|private[_-]?key|credential)", re.I
)
MAX_CHECKPOINT_BYTES = 256 * 1024
SCHEMA_VERSION = 1


class CheckpointError(RuntimeError):
    """Raised when a checkpoint cannot be created, verified, or resumed."""


@dataclass(frozen=True)
class Checkpoint:
    checkpoint_id: str
    execution_id: str
    task_id: str
    attempt_number: int
    sequence: int
    parent_checkpoint_id: str | None
    state: Mapping[str, Any]
    metadata: Mapping[str, Any]
    created_at: float
    digest: str
    schema_version: int = SCHEMA_VERSION


@dataclass(frozen=True)
class ResumePlan:
    checkpoint_id: str
    execution_id: str
    task_id: str
    attempt_id: str
    attempt_number: int
    state: Mapping[str, Any]
    parent_checkpoint_id: str | None


def _reject_secrets(value: Any, path: str = "checkpoint") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            if _SECRET_KEY.search(key_text):
                raise CheckpointError(f"secret-like field rejected: {path}.{key_text}")
            _reject_secrets(child, f"{path}.{key_text}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_secrets(child, f"{path}[{index}]")


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class CheckpointStore:
    """Append-only SQLite checkpoint storage with hash verification and lineage."""

    def __init__(self, path: str | Path = ":memory:", event_bus: EventBus | None = None) -> None:
        self.path = str(path)
        self.event_bus = event_bus
        self._db = sqlite3.connect(self.path, isolation_level=None)
        self._db.row_factory = sqlite3.Row
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.executescript(
            """
            CREATE TABLE IF NOT EXISTS checkpoints (
                checkpoint_id TEXT PRIMARY KEY,
                execution_id TEXT NOT NULL,
                task_id TEXT NOT NULL,
                attempt_number INTEGER NOT NULL CHECK(attempt_number > 0),
                sequence INTEGER NOT NULL CHECK(sequence > 0),
                parent_checkpoint_id TEXT,
                state TEXT NOT NULL,
                metadata TEXT NOT NULL,
                created_at REAL NOT NULL,
                digest TEXT NOT NULL,
                schema_version INTEGER NOT NULL,
                UNIQUE(execution_id, sequence),
                FOREIGN KEY(parent_checkpoint_id) REFERENCES checkpoints(checkpoint_id)
            );
            CREATE INDEX IF NOT EXISTS ix_checkpoint_execution ON checkpoints(execution_id, sequence DESC);
            """
        )

    def close(self) -> None:
        self._db.close()

    @staticmethod
    def _digest(
        *, checkpoint_id: str, execution_id: str, task_id: str, attempt_number: int,
        sequence: int, parent_checkpoint_id: str | None, state: Mapping[str, Any],
        metadata: Mapping[str, Any], created_at: float, schema_version: int,
    ) -> str:
        envelope = {
            "checkpoint_id": checkpoint_id, "execution_id": execution_id, "task_id": task_id,
            "attempt_number": attempt_number, "sequence": sequence,
            "parent_checkpoint_id": parent_checkpoint_id, "state": state, "metadata": metadata,
            "created_at": created_at, "schema_version": schema_version,
        }
        return hashlib.sha256(_canonical(envelope).encode("utf-8")).hexdigest()

    @staticmethod
    def _row(row: sqlite3.Row) -> Checkpoint:
        return Checkpoint(
            row["checkpoint_id"], row["execution_id"], row["task_id"], row["attempt_number"],
            row["sequence"], row["parent_checkpoint_id"], json.loads(row["state"]),
            json.loads(row["metadata"]), row["created_at"], row["digest"], row["schema_version"],
        )

    def save(
        self, execution: Execution, state: Mapping[str, Any], *, metadata: Mapping[str, Any] | None = None,
        parent_checkpoint_id: str | None = None,
    ) -> Checkpoint:
        if not isinstance(state, Mapping):
            raise CheckpointError("state must be a mapping")
        metadata = dict(metadata or {})
        _reject_secrets(state)
        _reject_secrets(metadata, "metadata")
        encoded_state = _canonical(state)
        encoded_metadata = _canonical(metadata)
        if len(encoded_state.encode("utf-8")) + len(encoded_metadata.encode("utf-8")) > MAX_CHECKPOINT_BYTES:
            raise CheckpointError("checkpoint exceeds maximum serialized size")
        now = time.time()
        checkpoint_id = str(uuid.uuid4())
        self._db.execute("BEGIN IMMEDIATE")
        try:
            previous = self._db.execute(
                "SELECT sequence FROM checkpoints WHERE execution_id=? ORDER BY sequence DESC LIMIT 1",
                (execution.execution_id,),
            ).fetchone()
            sequence = (previous["sequence"] if previous else 0) + 1
            if parent_checkpoint_id is not None:
                parent = self._db.execute(
                    "SELECT execution_id, sequence FROM checkpoints WHERE checkpoint_id=?",
                    (parent_checkpoint_id,),
                ).fetchone()
                if parent is None or parent["execution_id"] != execution.execution_id or parent["sequence"] >= sequence:
                    raise CheckpointError("parent checkpoint is invalid or outside the execution lineage")
            digest = self._digest(
                checkpoint_id=checkpoint_id, execution_id=execution.execution_id, task_id=execution.task_id,
                attempt_number=execution.attempt_number, sequence=sequence,
                parent_checkpoint_id=parent_checkpoint_id, state=state, metadata=metadata,
                created_at=now, schema_version=SCHEMA_VERSION,
            )
            self._db.execute(
                "INSERT INTO checkpoints VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (checkpoint_id, execution.execution_id, execution.task_id, execution.attempt_number, sequence,
                 parent_checkpoint_id, encoded_state, encoded_metadata, now, digest, SCHEMA_VERSION),
            )
            self._db.execute("COMMIT")
        except Exception:
            self._db.execute("ROLLBACK")
            raise
        checkpoint = self.get(checkpoint_id)
        if self.event_bus is not None:
            self.event_bus.append(
                "execution.checkpoint_created", "execution", execution.execution_id,
                {"checkpoint_id": checkpoint_id, "sequence": sequence, "attempt_number": execution.attempt_number},
                correlation_id=execution.execution_id,
            )
        return checkpoint

    def get(self, checkpoint_id: str) -> Checkpoint:
        row = self._db.execute("SELECT * FROM checkpoints WHERE checkpoint_id=?", (checkpoint_id,)).fetchone()
        if row is None:
            raise CheckpointError(f"checkpoint {checkpoint_id} not found")
        return self._row(row)

    def latest(self, execution_id: str) -> Checkpoint | None:
        row = self._db.execute(
            "SELECT * FROM checkpoints WHERE execution_id=? ORDER BY sequence DESC LIMIT 1", (execution_id,)
        ).fetchone()
        return self._row(row) if row else None

    def list(self, execution_id: str) -> tuple[Checkpoint, ...]:
        rows = self._db.execute(
            "SELECT * FROM checkpoints WHERE execution_id=? ORDER BY sequence", (execution_id,)
        ).fetchall()
        return tuple(self._row(row) for row in rows)

    def verify(self, checkpoint_id: str) -> Checkpoint:
        checkpoint = self.get(checkpoint_id)
        expected = self._digest(
            checkpoint_id=checkpoint.checkpoint_id, execution_id=checkpoint.execution_id,
            task_id=checkpoint.task_id, attempt_number=checkpoint.attempt_number,
            sequence=checkpoint.sequence, parent_checkpoint_id=checkpoint.parent_checkpoint_id,
            state=checkpoint.state, metadata=checkpoint.metadata, created_at=checkpoint.created_at,
            schema_version=checkpoint.schema_version,
        )
        if expected != checkpoint.digest:
            raise CheckpointError("checkpoint integrity verification failed")
        if checkpoint.parent_checkpoint_id:
            parent = self.get(checkpoint.parent_checkpoint_id)
            if parent.execution_id != checkpoint.execution_id or parent.sequence >= checkpoint.sequence:
                raise CheckpointError("checkpoint lineage verification failed")
        return checkpoint

    def resume(self, checkpoint_id: str, execution_store: ExecutionStore) -> ResumePlan:
        checkpoint = self.verify(checkpoint_id)
        execution = execution_store.get(checkpoint.execution_id)
        if execution.task_id != checkpoint.task_id:
            raise CheckpointError("checkpoint task identity does not match execution")
        if execution.state not in {State.FAILED, State.EXPIRED, State.CANCELLED}:
            raise CheckpointError("resume requires a terminal failed, expired, or cancelled execution")
        attempt = execution_store.new_attempt(execution.execution_id)
        if self.event_bus is not None:
            self.event_bus.append(
                "execution.checkpoint_resumed", "execution", execution.execution_id,
                {"checkpoint_id": checkpoint.checkpoint_id, "new_attempt_id": attempt.attempt_id,
                 "new_attempt_number": attempt.number}, correlation_id=execution.execution_id,
            )
        return ResumePlan(
            checkpoint.checkpoint_id, execution.execution_id, execution.task_id,
            attempt.attempt_id, attempt.number, checkpoint.state, checkpoint.parent_checkpoint_id,
        )

    def verify_lineage(self, execution_id: str) -> tuple[Checkpoint, ...]:
        checkpoints = self.list(execution_id)
        previous_sequence = 0
        for checkpoint in checkpoints:
            self.verify(checkpoint.checkpoint_id)
            if checkpoint.sequence != previous_sequence + 1:
                raise CheckpointError("checkpoint sequence is not contiguous")
            previous_sequence = checkpoint.sequence
        return checkpoints
