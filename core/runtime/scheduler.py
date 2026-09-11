"""Phase 46 durable parallel scheduling and execution orchestration."""
from __future__ import annotations

import sqlite3
import threading
import time
import uuid
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from enum import StrEnum
from typing import Mapping

from core.runtime.events import EventBus
from core.runtime.execution import AuthorizedTask, Execution, ExecutionRuntime, State


class ScheduleState(StrEnum):
    WAITING = "waiting"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


TERMINAL_SCHEDULE = frozenset({ScheduleState.SUCCEEDED, ScheduleState.FAILED, ScheduleState.CANCELLED, ScheduleState.BLOCKED})


@dataclass(frozen=True)
class ScheduledItem:
    schedule_id: str
    execution_id: str
    task_id: str
    priority: int
    state: ScheduleState
    dependencies: tuple[str, ...]
    submitted_at: float
    started_at: float | None = None
    finished_at: float | None = None
    error: str | None = None


class ParallelScheduler:
    """Durable dependency-aware scheduler over the authoritative execution runtime."""

    def __init__(
        self, runtime: ExecutionRuntime, adapter: object, *, max_workers: int = 4,
        path: str = ":memory:", event_bus: EventBus | None = None,
        aging_seconds: float = 30.0, poll_seconds: float = 0.02,
    ) -> None:
        if max_workers < 1:
            raise ValueError("max_workers must be >= 1")
        if aging_seconds <= 0 or poll_seconds <= 0:
            raise ValueError("aging_seconds and poll_seconds must be > 0")
        self.runtime, self.adapter, self.max_workers = runtime, adapter, max_workers
        self.event_bus, self.aging_seconds, self.poll_seconds = event_bus, aging_seconds, poll_seconds
        self.path = path
        self._db = sqlite3.connect(path, check_same_thread=False, isolation_level=None)
        self._db.row_factory = sqlite3.Row
        self._lock = threading.RLock()
        self._wake, self._stop = threading.Event(), threading.Event()
        self._thread: threading.Thread | None = None
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="si-exec")
        self._futures: dict[str, Future[Execution]] = {}
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute("PRAGMA foreign_keys=ON")
        self._db.executescript("""
            CREATE TABLE IF NOT EXISTS schedules (
              schedule_id TEXT PRIMARY KEY, execution_id TEXT NOT NULL UNIQUE,
              task_id TEXT NOT NULL, priority INTEGER NOT NULL, state TEXT NOT NULL,
              submitted_at REAL NOT NULL, started_at REAL, finished_at REAL, error TEXT
            );
            CREATE TABLE IF NOT EXISTS schedule_dependencies (
              schedule_id TEXT NOT NULL REFERENCES schedules(schedule_id) ON DELETE CASCADE,
              dependency_execution_id TEXT NOT NULL,
              PRIMARY KEY(schedule_id, dependency_execution_id)
            );
            CREATE INDEX IF NOT EXISTS ix_schedules_ready ON schedules(state, priority, submitted_at);
            CREATE INDEX IF NOT EXISTS ix_schedule_deps ON schedule_dependencies(dependency_execution_id);
        """)
        self._recover_running()

    def close(self) -> None:
        self.stop()
        self._executor.shutdown(wait=True, cancel_futures=False)
        with self._lock:
            self._db.close()

    def submit(self, task: AuthorizedTask, *, depends_on: tuple[str, ...] = (), priority: int = 0) -> ScheduledItem:
        if not isinstance(priority, int) or isinstance(priority, bool):
            raise ValueError("priority must be an integer")
        if len(set(depends_on)) != len(depends_on):
            raise ValueError("depends_on must not contain duplicates")
        with self._lock:
            for dependency in depends_on:
                if self._db.execute("SELECT 1 FROM schedules WHERE execution_id=?", (dependency,)).fetchone() is None:
                    raise ValueError(f"unknown dependency execution: {dependency}")
        execution = self.runtime.accept(task)
        if execution.execution_id in depends_on:
            self.runtime.cancel(execution.execution_id)
            self.runtime.run(execution.execution_id, self.adapter)
            raise ValueError("an execution cannot depend on itself")
        schedule_id, now = str(uuid.uuid4()), time.time()
        with self._lock:
            try:
                self._db.execute("BEGIN IMMEDIATE")
                self._db.execute("INSERT INTO schedules VALUES (?, ?, ?, ?, ?, ?, NULL, NULL, NULL)", (schedule_id, execution.execution_id, task.task_id, priority, ScheduleState.WAITING.value, now))
                self._db.executemany("INSERT INTO schedule_dependencies VALUES (?, ?)", ((schedule_id, dep) for dep in depends_on))
                self._db.execute("COMMIT")
            except Exception:
                self._db.execute("ROLLBACK")
                self.runtime.cancel(execution.execution_id)
                self.runtime.run(execution.execution_id, self.adapter)
                raise
        self._emit(execution.execution_id, "scheduler.queued", {"schedule_id": schedule_id, "priority": priority, "dependencies": list(depends_on)})
        self._wake.set()
        return self.get(schedule_id)

    def get(self, schedule_id: str) -> ScheduledItem:
        with self._lock:
            row = self._db.execute("SELECT * FROM schedules WHERE schedule_id=?", (schedule_id,)).fetchone()
            if row is None:
                raise KeyError(schedule_id)
            deps = self._db.execute("SELECT dependency_execution_id FROM schedule_dependencies WHERE schedule_id=? ORDER BY dependency_execution_id", (schedule_id,)).fetchall()
        return ScheduledItem(row["schedule_id"], row["execution_id"], row["task_id"], row["priority"], ScheduleState(row["state"]), tuple(d[0] for d in deps), row["submitted_at"], row["started_at"], row["finished_at"], row["error"])

    def list(self, *, state: ScheduleState | None = None) -> tuple[ScheduledItem, ...]:
        with self._lock:
            rows = self._db.execute("SELECT schedule_id FROM schedules" + (" WHERE state=?" if state else "") + " ORDER BY submitted_at", (state.value,) if state else ()).fetchall()
        return tuple(self.get(row[0]) for row in rows)

    def cancel(self, schedule_id: str) -> ScheduledItem:
        item = self.get(schedule_id)
        if item.state in TERMINAL_SCHEDULE:
            return item
        self.runtime.cancel(item.execution_id)
        with self._lock:
            self._db.execute("UPDATE schedules SET state=?, finished_at=? WHERE schedule_id=? AND state NOT IN (?, ?, ?, ?)", (ScheduleState.CANCELLED.value, time.time(), schedule_id, *(s.value for s in TERMINAL_SCHEDULE)))
        if item.state == ScheduleState.WAITING:
            self.runtime.run(item.execution_id, self.adapter)
        self._emit(item.execution_id, "scheduler.cancelled", {"schedule_id": schedule_id})
        self._wake.set()
        return self.get(schedule_id)

    def start(self) -> None:
        with self._lock:
            if self._thread and self._thread.is_alive():
                return
            self._stop.clear()
            self._thread = threading.Thread(target=self._loop, name="si-scheduler", daemon=True)
            self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._wake.set()
        thread = self._thread
        if thread and thread.is_alive():
            thread.join(timeout=5)
        self._thread = None

    def drain(self, *, timeout: float = 10.0) -> tuple[ScheduledItem, ...]:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            self._dispatch_ready()
            self._reconcile()
            items = self.list()
            if items and all(item.state in TERMINAL_SCHEDULE for item in items):
                return items
            time.sleep(self.poll_seconds)
        raise TimeoutError("scheduler did not drain before timeout")

    def _loop(self) -> None:
        while not self._stop.is_set():
            self._dispatch_ready()
            self._reconcile()
            self._wake.wait(self.poll_seconds)
            self._wake.clear()

    def _dispatch_ready(self) -> None:
        with self._lock:
            active = sum(1 for future in self._futures.values() if not future.done())
        while active < self.max_workers:
            candidate = self._claim_ready()
            if candidate is None:
                return
            future = self._executor.submit(self.runtime.run, candidate.execution_id, self.adapter)
            with self._lock:
                self._futures[candidate.execution_id] = future
            active += 1

    def _claim_ready(self) -> ScheduledItem | None:
        now = time.time()
        with self._lock:
            rows = self._db.execute(
                "SELECT s.* FROM schedules s WHERE s.state=? AND NOT EXISTS "
                "(SELECT 1 FROM schedule_dependencies d JOIN schedules dep ON dep.execution_id=d.dependency_execution_id "
                "WHERE d.schedule_id=s.schedule_id AND dep.state NOT IN (?, ?, ?, ?)) "
                "ORDER BY (s.priority + CAST((? - s.submitted_at) / ? AS INTEGER)) DESC, s.submitted_at, s.schedule_id",
                (ScheduleState.WAITING.value, *(s.value for s in TERMINAL_SCHEDULE), now, self.aging_seconds),
            ).fetchall()
            for row in rows:
                deps = self._db.execute("SELECT dependency_execution_id FROM schedule_dependencies WHERE schedule_id=?", (row["schedule_id"],)).fetchall()
                blocked = any(
                    (dep_state := self._db.execute("SELECT state FROM schedules WHERE execution_id=?", (dep[0],)).fetchone())
                    and ScheduleState(dep_state[0]) in {ScheduleState.FAILED, ScheduleState.CANCELLED, ScheduleState.BLOCKED}
                    for dep in deps
                )
                if blocked:
                    self._db.execute("UPDATE schedules SET state=?, finished_at=?, error=? WHERE schedule_id=? AND state=?", (ScheduleState.BLOCKED.value, now, "dependency_failed", row["schedule_id"], ScheduleState.WAITING.value))
                    self.runtime.cancel(row["execution_id"])
                    self.runtime.run(row["execution_id"], self.adapter)
                    self._emit(row["execution_id"], "scheduler.blocked", {"schedule_id": row["schedule_id"], "reason": "dependency_failed"})
                    continue
                changed = self._db.execute("UPDATE schedules SET state=?, started_at=? WHERE schedule_id=? AND state=?", (ScheduleState.RUNNING.value, now, row["schedule_id"], ScheduleState.WAITING.value)).rowcount
                if changed:
                    item = self.get(row["schedule_id"])
                    self._emit(item.execution_id, "scheduler.started", {"schedule_id": item.schedule_id})
                    return item
        return None

    def _reconcile(self) -> None:
        with self._lock:
            finished = [(execution_id, future) for execution_id, future in self._futures.items() if future.done()]
        for execution_id, future in finished:
            try:
                execution = future.result()
                state = {State.SUCCEEDED: ScheduleState.SUCCEEDED, State.FAILED: ScheduleState.FAILED, State.CANCELLED: ScheduleState.CANCELLED, State.EXPIRED: ScheduleState.FAILED}[execution.state]
                error = execution.error_code
            except Exception as exc:
                state, error = ScheduleState.FAILED, type(exc).__name__
            with self._lock:
                row = self._db.execute("SELECT schedule_id, state FROM schedules WHERE execution_id=?", (execution_id,)).fetchone()
                if row and ScheduleState(row["state"]) == ScheduleState.RUNNING:
                    self._db.execute("UPDATE schedules SET state=?, finished_at=?, error=? WHERE schedule_id=? AND state=?", (state.value, time.time(), error, row["schedule_id"], ScheduleState.RUNNING.value))
            if row:
                self._emit(execution_id, f"scheduler.{state.value}", {"schedule_id": row["schedule_id"], "error": error})
            with self._lock:
                self._futures.pop(execution_id, None)

    def _recover_running(self) -> None:
        with self._lock:
            rows = self._db.execute("SELECT schedule_id, execution_id FROM schedules WHERE state=?", (ScheduleState.RUNNING.value,)).fetchall()
            for row in rows:
                self._db.execute("UPDATE schedules SET state=?, started_at=NULL WHERE schedule_id=?", (ScheduleState.WAITING.value, row["schedule_id"]))
        if rows:
            self.runtime.recover()
            for row in rows:
                self._emit(row["execution_id"], "scheduler.recovered", {"schedule_id": row["schedule_id"]})

    def _emit(self, execution_id: str, event_type: str, payload: Mapping[str, object]) -> None:
        if self.event_bus is not None:
            self.event_bus.append(event_type, "execution", execution_id, payload, correlation_id=execution_id)
