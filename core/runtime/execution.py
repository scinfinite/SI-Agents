"""Durable Phase 44 execution runtime.

Authorization, admission, governance and provenance remain upstream in the
Control API. This module owns execution mechanics only.
"""
from __future__ import annotations

import json
import re
import sqlite3
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any, Mapping, Protocol


class State(StrEnum):
    ACCEPTED = "accepted"
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


TERMINAL = frozenset({State.SUCCEEDED, State.FAILED, State.CANCELLED, State.EXPIRED})
TRANSITIONS: dict[State, frozenset[State]] = {
    State.ACCEPTED: frozenset({State.QUEUED, State.CANCELLED, State.EXPIRED}),
    State.QUEUED: frozenset({State.RUNNING, State.CANCELLED, State.EXPIRED}),
    State.RUNNING: frozenset({State.SUCCEEDED, State.FAILED, State.CANCELLED, State.EXPIRED}),
    State.SUCCEEDED: frozenset(), State.FAILED: frozenset(), State.CANCELLED: frozenset(), State.EXPIRED: frozenset(),
}
_SECRET_KEY = re.compile(r"(?:password|passwd|secret|token|api[_-]?key|private[_-]?key|credential)", re.I)


@dataclass(frozen=True)
class AuthorizedTask:
    task_id: str
    payload: Mapping[str, Any]
    execution_id: str | None = None
    idempotency_key: str | None = None
    deadline_at: float | None = None
    authority_scope: str | None = None
    capability: str | None = None
    secret_refs: tuple[str, ...] = ()

    def validate(self) -> None:
        if not self.task_id:
            raise RuntimeFailure(RuntimeErrorCode.INVALID_REQUEST, "task_id is required")
        if self.deadline_at is not None and self.deadline_at <= 0:
            raise RuntimeFailure(RuntimeErrorCode.INVALID_REQUEST, "deadline_at must be an epoch timestamp")
        if self.idempotency_key == "":
            raise RuntimeFailure(RuntimeErrorCode.INVALID_REQUEST, "idempotency_key cannot be empty")
        _reject_inline_secrets(self.payload)


@dataclass(frozen=True)
class Attempt:
    attempt_id: str
    execution_id: str
    number: int
    state: State
    started_at: float | None = None
    finished_at: float | None = None
    error_code: str | None = None
    result: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class Execution:
    execution_id: str
    task_id: str
    state: State
    attempt_id: str
    attempt_number: int
    idempotency_key: str | None
    deadline_at: float | None
    cancel_requested: bool
    pause_requested: bool
    result: Mapping[str, Any] | None = None
    error_code: str | None = None


class RuntimeAdapter(Protocol):
    """Mechanics adapter; it cannot authorize work or alter provenance."""
    def invoke(self, task: AuthorizedTask, cancel_event: threading.Event) -> Mapping[str, Any]: ...
    def cancel(self, execution_id: str) -> None: ...
    def pause(self, execution_id: str) -> None: ...
    def resume(self, execution_id: str) -> None: ...


class RuntimeErrorCode(StrEnum):
    INVALID_REQUEST = "invalid_request"
    INVALID_TRANSITION = "invalid_transition"
    NOT_FOUND = "not_found"
    IDEMPOTENCY_CONFLICT = "idempotency_conflict"
    DEADLINE_EXCEEDED = "deadline_exceeded"
    CANCELLED = "cancelled"
    ADAPTER_FAILURE = "adapter_failure"
    SECRET_LEAK = "secret_leak"
    PAUSE_UNSUPPORTED = "pause_unsupported"


class RuntimeFailure(RuntimeError):
    def __init__(self, code: RuntimeErrorCode, message: str):
        super().__init__(message)
        self.code = code


def _reject_inline_secrets(value: Any, path: str = "payload") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            if _SECRET_KEY.search(key_text):
                raise RuntimeFailure(RuntimeErrorCode.SECRET_LEAK, f"inline secret-like field rejected: {path}.{key_text}")
            _reject_inline_secrets(child, f"{path}.{key_text}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_inline_secrets(child, f"{path}[{index}]")


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class ExecutionStore:
    """SQLite-backed durable execution state with atomic terminal transitions."""
    def __init__(self, path: str | Path = ":memory:") -> None:
        self.path = str(path)
        self._db = sqlite3.connect(self.path, check_same_thread=False, isolation_level=None)
        self._db.row_factory = sqlite3.Row
        self._lock = threading.RLock()
        self._db.execute("PRAGMA foreign_keys=ON")
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.executescript("""
            CREATE TABLE IF NOT EXISTS executions (
                execution_id TEXT PRIMARY KEY, task_id TEXT NOT NULL, payload TEXT NOT NULL,
                state TEXT NOT NULL, attempt_id TEXT NOT NULL, attempt_number INTEGER NOT NULL,
                idempotency_key TEXT, deadline_at REAL, cancel_requested INTEGER NOT NULL DEFAULT 0,
                pause_requested INTEGER NOT NULL DEFAULT 0, result TEXT, error_code TEXT,
                created_at REAL NOT NULL, updated_at REAL NOT NULL
            );
            CREATE UNIQUE INDEX IF NOT EXISTS ux_execution_idempotency
                ON executions(task_id, idempotency_key) WHERE idempotency_key IS NOT NULL;
            CREATE INDEX IF NOT EXISTS ix_execution_state ON executions(state);
            CREATE TABLE IF NOT EXISTS attempts (
                attempt_id TEXT PRIMARY KEY, execution_id TEXT NOT NULL REFERENCES executions(execution_id),
                number INTEGER NOT NULL, state TEXT NOT NULL, started_at REAL, finished_at REAL,
                error_code TEXT, result TEXT, UNIQUE(execution_id, number)
            );
        """)

    def close(self) -> None:
        with self._lock:
            self._db.close()

    def create(self, task: AuthorizedTask) -> Execution:
        task.validate()
        now = time.time()
        with self._lock:
            if task.idempotency_key:
                row = self._db.execute("SELECT * FROM executions WHERE task_id=? AND idempotency_key=?", (task.task_id, task.idempotency_key)).fetchone()
                if row:
                    if row["payload"] != _json(task.payload) or row["deadline_at"] != task.deadline_at:
                        raise RuntimeFailure(RuntimeErrorCode.IDEMPOTENCY_CONFLICT, "idempotency key conflicts with existing execution")
                    return self._execution(row)
            execution_id, attempt_id = task.execution_id or str(uuid.uuid4()), str(uuid.uuid4())
            try:
                self._db.execute("BEGIN IMMEDIATE")
                self._db.execute("INSERT INTO executions VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 0, NULL, NULL, ?, ?)", (execution_id, task.task_id, _json(task.payload), State.ACCEPTED.value, attempt_id, 1, task.idempotency_key, task.deadline_at, now, now))
                self._db.execute("INSERT INTO attempts VALUES (?, ?, 1, ?, NULL, NULL, NULL, NULL)", (attempt_id, execution_id, State.ACCEPTED.value))
                self._db.execute("COMMIT")
            except sqlite3.IntegrityError as exc:
                self._db.execute("ROLLBACK")
                if task.idempotency_key:
                    row = self._db.execute("SELECT * FROM executions WHERE task_id=? AND idempotency_key=?", (task.task_id, task.idempotency_key)).fetchone()
                    if row and row["payload"] == _json(task.payload):
                        return self._execution(row)
                raise RuntimeFailure(RuntimeErrorCode.IDEMPOTENCY_CONFLICT, str(exc)) from exc
            return self.get(execution_id)

    def get(self, execution_id: str) -> Execution:
        with self._lock:
            row = self._db.execute("SELECT * FROM executions WHERE execution_id=?", (execution_id,)).fetchone()
        if row is None:
            raise RuntimeFailure(RuntimeErrorCode.NOT_FOUND, f"execution {execution_id} not found")
        return self._execution(row)

    @staticmethod
    def _execution(row: sqlite3.Row) -> Execution:
        return Execution(row["execution_id"], row["task_id"], State(row["state"]), row["attempt_id"], row["attempt_number"], row["idempotency_key"], row["deadline_at"], bool(row["cancel_requested"]), bool(row["pause_requested"]), json.loads(row["result"]) if row["result"] else None, row["error_code"])

    def transition(self, execution_id: str, target: State, *, error_code: str | None = None, result: Mapping[str, Any] | None = None) -> Execution:
        with self._lock:
            row = self._db.execute("SELECT state, attempt_id FROM executions WHERE execution_id=?", (execution_id,)).fetchone()
            if row is None:
                raise RuntimeFailure(RuntimeErrorCode.NOT_FOUND, f"execution {execution_id} not found")
            current = State(row["state"])
            if current == target and current in TERMINAL:
                return self.get(execution_id)
            if target not in TRANSITIONS[current]:
                raise RuntimeFailure(RuntimeErrorCode.INVALID_TRANSITION, f"{current.value} -> {target.value} is not allowed")
            encoded = _json(result) if result is not None else None
            now = time.time()
            changed = self._db.execute("UPDATE executions SET state=?, result=?, error_code=?, updated_at=? WHERE execution_id=? AND state=?", (target.value, encoded, error_code, now, execution_id, current.value)).rowcount
            if changed != 1:
                return self.get(execution_id)
            self._db.execute("UPDATE attempts SET state=?, finished_at=?, error_code=?, result=? WHERE attempt_id=?", (target.value, now if target in TERMINAL else None, error_code, encoded, row["attempt_id"]))
            return self.get(execution_id)

    def request_cancel(self, execution_id: str) -> Execution:
        with self._lock:
            self._db.execute("UPDATE executions SET cancel_requested=1, updated_at=? WHERE execution_id=?", (time.time(), execution_id))
        return self.get(execution_id)

    def request_pause(self, execution_id: str) -> Execution:
        with self._lock:
            self._db.execute("UPDATE executions SET pause_requested=1, updated_at=? WHERE execution_id=?", (time.time(), execution_id))
        return self.get(execution_id)

    def clear_pause(self, execution_id: str) -> Execution:
        with self._lock:
            self._db.execute("UPDATE executions SET pause_requested=0, updated_at=? WHERE execution_id=?", (time.time(), execution_id))
        return self.get(execution_id)

    def new_attempt(self, execution_id: str) -> Attempt:
        with self._lock:
            row = self._db.execute("SELECT * FROM executions WHERE execution_id=?", (execution_id,)).fetchone()
            if row is None:
                raise RuntimeFailure(RuntimeErrorCode.NOT_FOUND, f"execution {execution_id} not found")
            if State(row["state"]) not in {State.FAILED, State.EXPIRED, State.CANCELLED}:
                raise RuntimeFailure(RuntimeErrorCode.INVALID_TRANSITION, "retry requires a terminal execution")
            number, attempt_id, now = row["attempt_number"] + 1, str(uuid.uuid4()), time.time()
            self._db.execute("BEGIN IMMEDIATE")
            self._db.execute("UPDATE executions SET attempt_id=?, attempt_number=?, state=?, result=NULL, error_code=NULL, cancel_requested=0, pause_requested=0, updated_at=? WHERE execution_id=?", (attempt_id, number, State.QUEUED.value, now, execution_id))
            self._db.execute("INSERT INTO attempts VALUES (?, ?, ?, ?, NULL, NULL, NULL, NULL)", (attempt_id, execution_id, number, State.QUEUED.value))
            self._db.execute("COMMIT")
            return Attempt(attempt_id, execution_id, number, State.QUEUED)

    def recover(self) -> tuple[Execution, ...]:
        with self._lock:
            rows = self._db.execute("SELECT execution_id FROM executions WHERE state=?", (State.RUNNING.value,)).fetchall()
            for row in rows:
                self._db.execute("UPDATE executions SET state=?, updated_at=? WHERE execution_id=? AND state=?", (State.QUEUED.value, time.time(), row["execution_id"], State.RUNNING.value))
                self._db.execute("UPDATE attempts SET state=? WHERE execution_id=? AND state=?", (State.QUEUED.value, row["execution_id"], State.RUNNING.value))
        return tuple(self.get(row["execution_id"]) for row in rows)

    def list_non_terminal(self) -> tuple[Execution, ...]:
        with self._lock:
            rows = self._db.execute("SELECT * FROM executions WHERE state NOT IN (?, ?, ?, ?) ORDER BY created_at", tuple(s.value for s in TERMINAL)).fetchall()
        return tuple(self._execution(row) for row in rows)


@dataclass
class _Control:
    cancel: threading.Event = field(default_factory=threading.Event)


class ExecutionRuntime:
    def __init__(self, store: ExecutionStore):
        self.store = store
        self._controls: dict[str, _Control] = {}
        self._lock = threading.RLock()

    def accept(self, task: AuthorizedTask) -> Execution:
        execution = self.store.create(task)
        if execution.state == State.ACCEPTED:
            self.store.transition(execution.execution_id, State.QUEUED)
        return self.store.get(execution.execution_id)

    def cancel(self, execution_id: str) -> Execution:
        execution = self.store.request_cancel(execution_id)
        self._control(execution_id).cancel.set()
        return execution

    def pause(self, execution_id: str, adapter: RuntimeAdapter) -> Execution:
        execution = self.store.request_pause(execution_id)
        if execution.state == State.RUNNING:
            pause = getattr(adapter, "pause", None)
            if pause is None:
                self.store.clear_pause(execution_id)
                raise RuntimeFailure(RuntimeErrorCode.PAUSE_UNSUPPORTED, "adapter does not support pause")
            pause(execution_id)
        return self.store.get(execution_id)

    def resume(self, execution_id: str, adapter: RuntimeAdapter) -> Execution:
        execution = self.store.get(execution_id)
        resume = getattr(adapter, "resume", None)
        if execution.pause_requested and resume is None:
            raise RuntimeFailure(RuntimeErrorCode.PAUSE_UNSUPPORTED, "adapter does not support resume")
        self.store.clear_pause(execution_id)
        if resume is not None:
            resume(execution_id)
        return self.store.get(execution_id)

    def retry(self, execution_id: str) -> Attempt:
        return self.store.new_attempt(execution_id)

    def recover(self) -> tuple[Execution, ...]:
        recovered = self.store.recover()
        with self._lock:
            for execution in recovered:
                self._controls.pop(execution.execution_id, None)
        return recovered

    def run(self, execution_id: str, adapter: RuntimeAdapter) -> Execution:
        execution = self.store.get(execution_id)
        if execution.state in TERMINAL:
            return execution
        control = self._control(execution_id)
        if execution.cancel_requested:
            control.cancel.set()
        if execution.pause_requested:
            return execution
        if execution.deadline_at is not None and time.time() >= execution.deadline_at:
            return self.store.transition(execution_id, State.EXPIRED, error_code=RuntimeErrorCode.DEADLINE_EXCEEDED.value)
        if execution.state == State.ACCEPTED:
            self.store.transition(execution_id, State.QUEUED)
        self.store.transition(execution_id, State.RUNNING)
        if control.cancel.is_set():
            self._cancel_adapter(adapter, execution_id)
            return self.store.transition(execution_id, State.CANCELLED, error_code=RuntimeErrorCode.CANCELLED.value)
        try:
            result = adapter.invoke(self._task_for(execution_id), control.cancel)
            latest = self.store.get(execution_id)
            if control.cancel.is_set() or latest.cancel_requested:
                self._cancel_adapter(adapter, execution_id)
                return self.store.transition(execution_id, State.CANCELLED, error_code=RuntimeErrorCode.CANCELLED.value)
            if latest.deadline_at is not None and time.time() >= latest.deadline_at:
                self._cancel_adapter(adapter, execution_id)
                return self.store.transition(execution_id, State.EXPIRED, error_code=RuntimeErrorCode.DEADLINE_EXCEEDED.value)
            return self.store.transition(execution_id, State.SUCCEEDED, result=dict(result))
        except Exception as exc:
            latest = self.store.get(execution_id)
            if control.cancel.is_set() or latest.cancel_requested:
                self._cancel_adapter(adapter, execution_id)
                return self.store.transition(execution_id, State.CANCELLED, error_code=RuntimeErrorCode.CANCELLED.value)
            return self.store.transition(execution_id, State.FAILED, error_code=RuntimeErrorCode.ADAPTER_FAILURE.value, result={"error": type(exc).__name__})
        finally:
            with self._lock:
                self._controls.pop(execution_id, None)

    def _task_for(self, execution_id: str) -> AuthorizedTask:
        with self.store._lock:
            row = self.store._db.execute("SELECT * FROM executions WHERE execution_id=?", (execution_id,)).fetchone()
        if row is None:
            raise RuntimeFailure(RuntimeErrorCode.NOT_FOUND, f"execution {execution_id} not found")
        return AuthorizedTask(task_id=row["task_id"], payload=json.loads(row["payload"]), execution_id=execution_id, idempotency_key=row["idempotency_key"], deadline_at=row["deadline_at"])

    def _control(self, execution_id: str) -> _Control:
        with self._lock:
            return self._controls.setdefault(execution_id, _Control())

    @staticmethod
    def _cancel_adapter(adapter: RuntimeAdapter, execution_id: str) -> None:
        try:
            adapter.cancel(execution_id)
        except Exception:
            pass
