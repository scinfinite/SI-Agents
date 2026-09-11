"""Durable Phase 45 event bus, replay, subscriptions, and projections."""
from __future__ import annotations

import json
import sqlite3
import threading
import time
import uuid
from dataclasses import dataclass
from typing import Any, Callable, Mapping


@dataclass(frozen=True)
class RuntimeEventRecord:
    event_id: str
    event_type: str
    aggregate_type: str
    aggregate_id: str
    sequence: int
    occurred_at: float
    correlation_id: str
    causation_id: str | None
    payload: Mapping[str, Any]


Subscriber = Callable[[RuntimeEventRecord], None]


class EventBus:
    """Append-only durable event log with ordered streams and projections."""

    def __init__(self, path: str = ":memory:") -> None:
        self.path = path
        self._db = sqlite3.connect(path, check_same_thread=False, isolation_level=None)
        self._db.row_factory = sqlite3.Row
        self._lock = threading.RLock()
        self._subscribers: dict[str, Subscriber] = {}
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.executescript("""
        CREATE TABLE IF NOT EXISTS runtime_events (
          event_id TEXT PRIMARY KEY, event_type TEXT NOT NULL,
          aggregate_type TEXT NOT NULL, aggregate_id TEXT NOT NULL,
          sequence INTEGER NOT NULL, occurred_at REAL NOT NULL,
          correlation_id TEXT NOT NULL, causation_id TEXT,
          payload TEXT NOT NULL,
          UNIQUE(aggregate_type, aggregate_id, sequence)
        );
        CREATE INDEX IF NOT EXISTS ix_runtime_events_correlation ON runtime_events(correlation_id, occurred_at);
        CREATE INDEX IF NOT EXISTS ix_runtime_events_aggregate ON runtime_events(aggregate_type, aggregate_id, sequence);
        CREATE TABLE IF NOT EXISTS event_projections (
          projection_name TEXT NOT NULL, aggregate_type TEXT NOT NULL,
          aggregate_id TEXT NOT NULL, version INTEGER NOT NULL,
          state TEXT NOT NULL, updated_at REAL NOT NULL,
          PRIMARY KEY(projection_name, aggregate_type, aggregate_id)
        );
        CREATE TABLE IF NOT EXISTS projection_checkpoints (
          projection_name TEXT PRIMARY KEY, last_event_id TEXT, last_occurred_at REAL,
          updated_at REAL NOT NULL
        );
        """)

    def close(self) -> None:
        with self._lock:
            self._db.close()
            self._subscribers.clear()

    def subscribe(self, callback: Subscriber) -> str:
        if not callable(callback):
            raise ValueError("subscriber must be callable")
        token = str(uuid.uuid4())
        with self._lock:
            self._subscribers[token] = callback
        return token

    def unsubscribe(self, token: str) -> bool:
        with self._lock:
            return self._subscribers.pop(token, None) is not None

    def append(
        self, event_type: str, aggregate_type: str, aggregate_id: str,
        payload: Mapping[str, Any], *, correlation_id: str | None = None,
        causation_id: str | None = None, event_id: str | None = None,
    ) -> RuntimeEventRecord:
        if not event_type.strip() or not aggregate_type.strip() or not aggregate_id.strip():
            raise ValueError("event_type, aggregate_type, and aggregate_id are required")
        if correlation_id is not None and not correlation_id.strip():
            raise ValueError("correlation_id must not be empty")
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        with self._lock:
            self._db.execute("BEGIN IMMEDIATE")
            try:
                if event_id:
                    existing = self._db.execute("SELECT * FROM runtime_events WHERE event_id=?", (event_id,)).fetchone()
                    if existing:
                        if existing["payload"] != encoded or existing["event_type"] != event_type or existing["aggregate_id"] != aggregate_id:
                            raise ValueError("event_id conflicts with existing event")
                        self._db.execute("COMMIT")
                        return self._record(existing)
                row = self._db.execute("SELECT COALESCE(MAX(sequence), -1) AS seq FROM runtime_events WHERE aggregate_type=? AND aggregate_id=?", (aggregate_type, aggregate_id)).fetchone()
                sequence = int(row["seq"]) + 1
                record = (event_id or str(uuid.uuid4()), event_type, aggregate_type, aggregate_id, sequence, time.time(), correlation_id or str(uuid.uuid4()), causation_id, encoded)
                self._db.execute("INSERT INTO runtime_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", record)
                self._db.execute("COMMIT")
            except Exception:
                self._db.execute("ROLLBACK")
                raise
            event = RuntimeEventRecord(record[0], record[1], record[2], record[3], record[4], record[5], record[6], record[7], payload)
            subscribers = tuple(self._subscribers.values())
        for subscriber in subscribers:
            try:
                subscriber(event)
            except Exception:
                pass
        return event

    def _record(self, row: sqlite3.Row) -> RuntimeEventRecord:
        return RuntimeEventRecord(row["event_id"], row["event_type"], row["aggregate_type"], row["aggregate_id"], row["sequence"], row["occurred_at"], row["correlation_id"], row["causation_id"], json.loads(row["payload"]))

    def stream(self, aggregate_type: str, aggregate_id: str, after_sequence: int = -1) -> tuple[RuntimeEventRecord, ...]:
        if after_sequence < -1:
            raise ValueError("after_sequence must be >= -1")
        with self._lock:
            rows = self._db.execute("SELECT * FROM runtime_events WHERE aggregate_type=? AND aggregate_id=? AND sequence>? ORDER BY sequence", (aggregate_type, aggregate_id, after_sequence)).fetchall()
        return tuple(self._record(row) for row in rows)

    def by_correlation(self, correlation_id: str) -> tuple[RuntimeEventRecord, ...]:
        with self._lock:
            rows = self._db.execute("SELECT * FROM runtime_events WHERE correlation_id=? ORDER BY occurred_at, rowid", (correlation_id,)).fetchall()
        return tuple(self._record(row) for row in rows)

    def replay(self, handler: Callable[[RuntimeEventRecord], None], *, after_event_id: str | None = None) -> int:
        with self._lock:
            rows = self._db.execute("SELECT * FROM runtime_events ORDER BY occurred_at, rowid").fetchall()
        started = after_event_id is None
        count = 0
        for row in rows:
            if not started:
                started = row["event_id"] == after_event_id
                continue
            handler(self._record(row))
            count += 1
        return count

    def project(self, projection_name: str, handler: Callable[[Mapping[str, Any], RuntimeEventRecord], Mapping[str, Any]]) -> int:
        if not projection_name.strip():
            raise ValueError("projection_name is required")
        with self._lock:
            checkpoint = self._db.execute("SELECT last_event_id FROM projection_checkpoints WHERE projection_name=?", (projection_name,)).fetchone()
            last = checkpoint["last_event_id"] if checkpoint else None
        processed = 0
        for event in self._events_after(last):
            with self._lock:
                row = self._db.execute("SELECT state FROM event_projections WHERE projection_name=? AND aggregate_type=? AND aggregate_id=?", (projection_name, event.aggregate_type, event.aggregate_id)).fetchone()
                current = json.loads(row["state"]) if row else {}
                new_state = handler(current, event)
                now = time.time()
                self._db.execute("BEGIN IMMEDIATE")
                try:
                    self._db.execute("INSERT INTO event_projections VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT(projection_name, aggregate_type, aggregate_id) DO UPDATE SET version=excluded.version, state=excluded.state, updated_at=excluded.updated_at", (projection_name, event.aggregate_type, event.aggregate_id, event.sequence + 1, json.dumps(new_state, sort_keys=True, separators=(",", ":")), now))
                    self._db.execute("INSERT INTO projection_checkpoints(projection_name,last_event_id,last_occurred_at,updated_at) VALUES(?,?,?,?) ON CONFLICT(projection_name) DO UPDATE SET last_event_id=excluded.last_event_id,last_occurred_at=excluded.last_occurred_at,updated_at=excluded.updated_at", (projection_name, event.event_id, event.occurred_at, now))
                    self._db.execute("COMMIT")
                except Exception:
                    self._db.execute("ROLLBACK")
                    raise
            processed += 1
        return processed

    def _events_after(self, event_id: str | None) -> tuple[RuntimeEventRecord, ...]:
        with self._lock:
            rows = self._db.execute("SELECT * FROM runtime_events ORDER BY occurred_at, rowid").fetchall()
        if event_id is None:
            return tuple(self._record(row) for row in rows)
        found = False
        output = []
        for row in rows:
            if found:
                output.append(self._record(row))
            elif row["event_id"] == event_id:
                found = True
        return tuple(output)

    def get_projection(self, projection_name: str, aggregate_type: str, aggregate_id: str) -> Mapping[str, Any] | None:
        with self._lock:
            row = self._db.execute("SELECT state FROM event_projections WHERE projection_name=? AND aggregate_type=? AND aggregate_id=?", (projection_name, aggregate_type, aggregate_id)).fetchone()
        return json.loads(row["state"]) if row else None

    def event_count(self) -> int:
        with self._lock:
            return int(self._db.execute("SELECT COUNT(*) FROM runtime_events").fetchone()[0])
