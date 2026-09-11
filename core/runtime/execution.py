"""Durable Phase 44 execution primitives.

This module deliberately contains no authorization or provider policy. A caller
must present an already-authorized task; the runtime only executes it and
normalizes lifecycle state.
"""
from __future__ import annotations

import json
import sqlite3
import threading
import time
import uuid
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Protocol


class State(StrEnum):
    ACCEPTED = "accepted"
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


TERMINAL = frozenset({State.SUCCEEDED, State.FAILED, State.CANCELLED, State.EXPIRED})
TRANSITIONS = {
    State.ACCEPTED: {State.QUEUED, State.CANCELLED, State.EXPIRED},
    State.QUEUED: {State.RUNNING, State.CANCELLED, State.EXPIRED},
    State.RUNNING: TERMINAL,
    State.SUCCEEDED: frozenset(),
    State.FAILED: frozenset(),
    State.CANCELLED: frozenset(),
    State.EXPIRED: frozenset(),
}


@dataclass(frozen=True, slots=True)
class AuthorizedTask:
    task_id: str
    execution_id: str
    payload: dict[str, object]
    deadline_epoch: float | None = None


@dataclass(frozen=True, slots=True)
class Attempt:
    attempt_id: str
    task_id: str
    execution_id: str
    state: State
    result: object = None
    error: str | None = None


class RuntimeAdapter(Protocol):
    def invoke(self, task: AuthorizedTask, *, cancel: threading.Event) -> object: ...

    def cancel(self, task: AuthorizedTask) -> None: ...


class RuntimeErrorCode(StrEnum):
    INVALID_TRANSITION = "invalid_transition"
    NOT_FOUND = "not_found"
    IDEMPOTENCY_CONFLICT = "idempotency_conflict"
    DEADLINE_EXCEEDED = "deadline_exceeded"
    CANCELLED = "cancelled"
    ADAPTER_FAILURE = "adapter_failure"


class RuntimeFailure(RuntimeError):
    def __init__(self, code: RuntimeErrorCode, message: str) -> None:
        super().__init__(message)
        self.code = code


class ExecutionStore:
    """Small transactional SQLite store suitable for local and service use."""

    def __init__(self, path: str | Path = ":memory:") -> None:
        self._db = sqlite3.connect(str(path), check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._lock = threading.RLock()
        self._db.executescript("""
        CREATE TABLE IF NOT EXISTS executions (
          execution_id TEXT PRIMARY KEY, task_id TEXT NOT NULL, attempt_id TEXT NOT NULL,
          state TEXT NOT NULL, payload TEXT NOT NULL, deadline REAL, result TEXT,
          error TEXT, idempotency_key TEXT UNIQUE, cancel_requested INTEGER NOT NULL DEFAULT 0,
          created REAL NOT NULL, updated REAL NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_executions_state ON executions(state);
        """)
        self._db.commit()

    def create(self, task: AuthorizedTask, idempotency_key: str | None = None) -> Attempt:
        now = time.time()
        attempt_id = uuid.uuid4().hex
        with self._lock, self._db:
            if idempotency_key:
                row = self._db.execute("SELECT * FROM executions WHERE idempotency_key=?", (idempotency_key,)).fetchone()
                if row:
                    if row["task_id"] != task.task_id or row["payload"] != json.dumps(task.payload, sort_keys=True):
                        raise RuntimeFailure(RuntimeErrorCode.IDEMPOTENCY_CONFLICT, "idempotency key is bound to another task")
                    return self._attempt(row)
            self._db.execute(
                "INSERT INTO executions VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (task.execution_id, task.task_id, attempt_id, State.ACCEPTED.value,
                 json.dumps(task.payload, sort_keys=True), task.deadline_epoch, None, None,
                 idempotency_key, 0, now, now),
            )
        return Attempt(attempt_id, task.task_id, task.execution_id, State.ACCEPTED)

    def _attempt(self, row: sqlite3.Row) -> Attempt:
        result = json.loads(row["result"]) if row["result"] else None
        return Attempt(row["attempt_id"], row["task_id"], row["execution_id"], State(row["state"]), result, row["error"])

    def get(self, execution_id: str) -> Attempt:
        with self._lock:
            row = self._db.execute("SELECT * FROM executions WHERE execution_id=?", (execution_id,)).fetchone()
        if row is None:
            raise RuntimeFailure(RuntimeErrorCode.NOT_FOUND, execution_id)
        return self._attempt(row)

    def transition(self, execution_id: str, target: State, *, result: object = None, error: str | None = None) -> Attempt:
        with self._lock, self._db:
            row = self._db.execute("SELECT * FROM executions WHERE execution_id=?", (execution_id,)).fetchone()
            if row is None:
                raise RuntimeFailure(RuntimeErrorCode.NOT_FOUND, execution_id)
            current = State(row["state"])
            if target not in TRANSITIONS[current]:
                raise RuntimeFailure(RuntimeErrorCode.INVALID_TRANSITION, f"{current} -> {target}")
            self._db.execute("UPDATE executions SET state=?, result=?, error=?, updated=? WHERE execution_id=?",
                             (target.value, json.dumps(result, sort_keys=True) if result is not None else None, error, time.time(), execution_id))
            return self._attempt(self._db.execute("SELECT * FROM executions WHERE execution_id=?", (execution_id,)).fetchone())

    def request_cancel(self, execution_id: str) -> Attempt:
        with self._lock, self._db:
            row = self._db.execute("SELECT * FROM executions WHERE execution_id=?", (execution_id,)).fetchone()
            if row is None:
                raise RuntimeFailure(RuntimeErrorCode.NOT_FOUND, execution_id)
            if State(row["state"]) in TERMINAL:
                return self._attempt(row)
            self._db.execute("UPDATE executions SET cancel_requested=1, updated=? WHERE execution_id=?", (time.time(), execution_id))
            return self._attempt(self._db.execute("SELECT * FROM executions WHERE execution_id=?", (execution_id,)).fetchone())

    def cancel_requested(self, execution_id: str) -> bool:
        with self._lock:
            row = self._db.execute("SELECT cancel_requested FROM executions WHERE execution_id=?", (execution_id,)).fetchone()
        if row is None:
            raise RuntimeFailure(RuntimeErrorCode.NOT_FOUND, execution_id)
        return bool(row[0])


class ExecutionRuntime:
    """Lifecycle coordinator for authorized tasks."""

    def __init__(self, store: ExecutionStore, adapter: RuntimeAdapter) -> None:
        self.store = store
        self.adapter = adapter
        self._signals: dict[str, threading.Event] = {}
        self._lock = threading.RLock()

    def accept(self, task: AuthorizedTask, *, idempotency_key: str | None = None) -> Attempt:
        attempt = self.store.create(task, idempotency_key=idempotency_key)
        if attempt.state == State.ACCEPTED:
            self.store.transition(task.execution_id, State.QUEUED)
        return self.store.get(task.execution_id)

    def cancel(self, execution_id: str) -> Attempt:
        attempt = self.store.request_cancel(execution_id)
        with self._lock:
            signal = self._signals.get(execution_id)
            if signal:
                signal.set()
        return attempt

    def run(self, execution_id: str) -> Attempt:
        current = self.store.get(execution_id)
        if current.state in TERMINAL:
            return current
        row_task = self.store._db.execute("SELECT * FROM executions WHERE execution_id=?", (execution_id,)).fetchone()
        task = AuthorizedTask(row_task["task_id"], execution_id, json.loads(row_task["payload"]), row_task["deadline"])
        self.store.transition(execution_id, State.RUNNING)
        signal = threading.Event()
        with self._lock:
            self._signals[execution_id] = signal
        try:
            if self.store.cancel_requested(execution_id):
                raise RuntimeFailure(RuntimeErrorCode.CANCELLED, "cancel requested")
            if task.deadline_epoch is not None and time.time() >= task.deadline_epoch:
                raise RuntimeFailure(RuntimeErrorCode.DEADLINE_EXCEEDED, "deadline exceeded")
            result = self.adapter.invoke(task, cancel=signal)
            if signal.is_set() or self.store.cancel_requested(execution_id):
                try:
                    self.adapter.cancel(task)
                finally:
                    return self.store.transition(execution_id, State.CANCELLED, error="cancelled")
            if task.deadline_epoch is not None and time.time() >= task.deadline_epoch:
                return self.store.transition(execution_id, State.EXPIRED, error="deadline exceeded")
            return self.store.transition(execution_id, State.SUCCEEDED, result=result)
        except RuntimeFailure as exc:
            target = State.CANCELLED if exc.code == RuntimeErrorCode.CANCELLED else State.EXPIRED if exc.code == RuntimeErrorCode.DEADLINE_EXCEEDED else State.FAILED
            return self.store.transition(execution_id, target, error=f"{exc.code}: {exc}")
        except Exception as exc:
            return self.store.transition(execution_id, State.FAILED, error=f"{RuntimeErrorCode.ADAPTER_FAILURE}: {exc}")
        finally:
            with self._lock:
                self._signals.pop(execution_id, None)
