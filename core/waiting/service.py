"""Durable, restart-safe waits and schedules owned by SI Core."""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from pathlib import Path
from threading import RLock
from uuid import uuid4

_MAX_PAYLOAD = 16_384
_MAX_QUEUE = 10_000
_MAX_INTERVAL = 365 * 24 * 3600


class WaitState(StrEnum):
    WAITING = "waiting"
    READY = "ready"
    CLAIMED = "claimed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class WaitKind(StrEnum):
    TIMER = "timer"
    DELAYED = "delayed"
    RECURRING = "recurring"
    CRON = "cron"
    APPROVAL = "approval"
    HUMAN = "human"
    DEPENDENCY = "dependency"
    RESOURCE = "resource"
    EXTERNAL = "external"


@dataclass(frozen=True)
class ScheduleSpec:
    """Validated recurrence policy; cron uses standard five-field UTC syntax."""

    kind: WaitKind
    interval_seconds: int | None = None
    cron: str | None = None
    max_occurrences: int | None = None

    def __post_init__(self) -> None:
        if self.kind is WaitKind.RECURRING:
            if self.interval_seconds is None or not 1 <= self.interval_seconds <= _MAX_INTERVAL:
                raise ValueError("interval_seconds must be between 1 and one year")
        if self.kind is WaitKind.CRON:
            if not self.cron or len(self.cron.split()) != 5:
                raise ValueError("cron must contain five fields")
            _validate_cron(self.cron)
        if self.max_occurrences is not None and not 1 <= self.max_occurrences <= _MAX_QUEUE:
            raise ValueError("max_occurrences is out of bounds")


@dataclass(frozen=True)
class WaitRecord:
    wait_id: str
    subject_id: str
    project_id: str
    kind: WaitKind
    state: WaitState
    wake_at: datetime
    created_at: datetime
    updated_at: datetime
    deadline: datetime | None
    priority: int
    created_sequence: int
    schedule: ScheduleSpec | None
    trigger: str | None
    payload: dict[str, object]
    occurrences: int
    revision: int

    def as_dict(self) -> dict[str, object]:
        return {
            "wait_id": self.wait_id,
            "subject_id": self.subject_id,
            "project_id": self.project_id,
            "kind": self.kind.value,
            "state": self.state.value,
            "wake_at": self.wake_at.isoformat(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "priority": self.priority,
            "created_sequence": self.created_sequence,
            "schedule": {
                "kind": self.schedule.kind.value,
                "interval_seconds": self.schedule.interval_seconds,
                "cron": self.schedule.cron,
                "max_occurrences": self.schedule.max_occurrences,
            } if self.schedule else None,
            "trigger": self.trigger,
            "payload": self.payload,
            "occurrences": self.occurrences,
            "revision": self.revision,
        }


class WaitingService:
    """SQLite-backed wait ledger and fair due-item scheduler."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()
        self._db = sqlite3.connect(self.path, check_same_thread=False, isolation_level=None)
        self._db.row_factory = sqlite3.Row
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute("PRAGMA busy_timeout=5000")
        self._db.executescript(
            """
            CREATE TABLE IF NOT EXISTS waits (
                wait_id TEXT PRIMARY KEY,
                subject_id TEXT NOT NULL,
                project_id TEXT NOT NULL,
                kind TEXT NOT NULL,
                state TEXT NOT NULL,
                wake_at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                deadline TEXT,
                priority INTEGER NOT NULL,
                created_sequence INTEGER NOT NULL,
                schedule_json TEXT,
                trigger TEXT,
                payload_json TEXT NOT NULL,
                occurrences INTEGER NOT NULL DEFAULT 0,
                revision INTEGER NOT NULL DEFAULT 1
            );
            CREATE INDEX IF NOT EXISTS waits_due ON waits(state, wake_at, priority, created_sequence);
            CREATE INDEX IF NOT EXISTS waits_scope ON waits(subject_id, project_id, state, wake_at);
            CREATE TABLE IF NOT EXISTS wait_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                wait_id TEXT NOT NULL,
                subject_id TEXT NOT NULL,
                project_id TEXT NOT NULL,
                event TEXT NOT NULL,
                at TEXT NOT NULL,
                metadata_json TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS wait_events_wait ON wait_events(wait_id, event_id);
            """
        )

    def create(self, *, subject_id: str, project_id: str, kind: WaitKind, wake_at: datetime,
               deadline: datetime | None = None, priority: int = 0, schedule: ScheduleSpec | None = None,
               trigger: str | None = None, payload: dict[str, object] | None = None,
               now: datetime | None = None) -> WaitRecord:
        subject_id = _identity(subject_id, "subject_id")
        project_id = _identity(project_id, "project_id")
        if not isinstance(kind, WaitKind):
            raise ValueError("invalid wait kind")
        wake_at = _utc(wake_at)
        deadline = _utc(deadline) if deadline else None
        if deadline and deadline <= wake_at:
            raise ValueError("deadline must be after wake_at")
        if not -100 <= priority <= 100:
            raise ValueError("priority must be between -100 and 100")
        if schedule and schedule.kind not in {WaitKind.RECURRING, WaitKind.CRON}:
            raise ValueError("schedule kind must be recurring or cron")
        if kind in {WaitKind.RECURRING, WaitKind.CRON} and schedule is None:
            raise ValueError("recurring and cron waits require a schedule")
        if kind not in {WaitKind.RECURRING, WaitKind.CRON} and schedule is not None:
            raise ValueError("one-shot waits cannot carry a schedule")
        payload = _safe_payload(payload or {})
        now = _utc(now or datetime.now(UTC))
        with self._lock:
            count = self._db.execute("SELECT COUNT(*) FROM waits WHERE state IN ('waiting','ready','claimed')").fetchone()[0]
            if count >= _MAX_QUEUE:
                raise RuntimeError("waiting queue capacity exceeded")
            sequence = self._db.execute("SELECT COALESCE(MAX(created_sequence), 0) + 1 FROM waits").fetchone()[0]
            wait_id = uuid4().hex
            stamp = now.isoformat()
            self._db.execute(
                "INSERT INTO waits VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (wait_id, subject_id, project_id, kind.value, WaitState.WAITING.value, wake_at.isoformat(), stamp,
                 stamp, deadline.isoformat() if deadline else None, priority, sequence, _schedule_json(schedule),
                 _clean_trigger(trigger), json.dumps(payload, sort_keys=True, separators=(",", ":")), 0, 1),
            )
            self._event(wait_id, subject_id, project_id, "created", now, {"kind": kind.value})
            return self.get(wait_id, subject_id=subject_id, project_id=project_id)

    def get(self, wait_id: str, *, subject_id: str, project_id: str) -> WaitRecord:
        row = self._scoped_row(wait_id, subject_id, project_id)
        if row is None:
            raise KeyError(wait_id)
        return _record(row)

    def list(self, *, subject_id: str, project_id: str, state: WaitState | None = None, limit: int = 100) -> list[WaitRecord]:
        _identity(subject_id, "subject_id")
        _identity(project_id, "project_id")
        if not 1 <= limit <= 500:
            raise ValueError("limit must be between 1 and 500")
        query = "SELECT * FROM waits WHERE subject_id=? AND project_id=?"
        args: list[object] = [subject_id, project_id]
        if state:
            query += " AND state=?"
            args.append(state.value)
        query += " ORDER BY wake_at, priority DESC, created_sequence LIMIT ?"
        args.append(limit)
        return [_record(row) for row in self._db.execute(query, args)]

    def promote_due(self, *, now: datetime | None = None, limit: int = 500) -> int:
        now = _utc(now or datetime.now(UTC))
        if not 1 <= limit <= 1000:
            raise ValueError("limit must be between 1 and 1000")
        changed = 0
        with self._lock:
            rows = self._db.execute("SELECT * FROM waits WHERE state='waiting' AND wake_at<=? ORDER BY wake_at LIMIT ?", (now.isoformat(), limit)).fetchall()
            for row in rows:
                state, event = (WaitState.EXPIRED, "expired") if row["deadline"] and row["deadline"] <= now.isoformat() else (WaitState.READY, "ready")
                self._db.execute("UPDATE waits SET state=?, updated_at=?, revision=revision+1 WHERE wait_id=? AND state='waiting'", (state.value, now.isoformat(), row["wait_id"]))
                self._event(row["wait_id"], row["subject_id"], row["project_id"], event, now, {})
                changed += 1
            deadline_rows = self._db.execute("SELECT * FROM waits WHERE state='waiting' AND deadline IS NOT NULL AND deadline<=? LIMIT ?", (now.isoformat(), limit)).fetchall()
            for row in deadline_rows:
                if row["wake_at"] > now.isoformat():
                    self._db.execute("UPDATE waits SET state='expired', updated_at=?, revision=revision+1 WHERE wait_id=? AND state='waiting'", (now.isoformat(), row["wait_id"]))
                    self._event(row["wait_id"], row["subject_id"], row["project_id"], "expired", now, {})
                    changed += 1
        return changed

    def claim_ready(self, *, subject_id: str, project_id: str, limit: int = 1, now: datetime | None = None) -> list[WaitRecord]:
        self.promote_due(now=now)
        now = _utc(now or datetime.now(UTC))
        if not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100")
        with self._lock:
            rows = self._db.execute("SELECT * FROM waits WHERE subject_id=? AND project_id=? AND state='ready'", (subject_id, project_id)).fetchall()
            def score(row: sqlite3.Row) -> tuple[float, int]:
                age = max(0.0, (now - _parse(row["created_at"])).total_seconds())
                return (row["priority"] + min(100.0, age / 60.0), -row["created_sequence"])
            rows = sorted(rows, key=score, reverse=True)[:limit]
            result: list[WaitRecord] = []
            for row in rows:
                cursor = self._db.execute("UPDATE waits SET state='claimed', updated_at=?, revision=revision+1 WHERE wait_id=? AND state='ready'", (now.isoformat(), row["wait_id"]))
                if cursor.rowcount != 1:
                    continue
                self._event(row["wait_id"], subject_id, project_id, "claimed", now, {})
                result.append(self.get(row["wait_id"], subject_id=subject_id, project_id=project_id))
            return result

    def complete(self, wait_id: str, *, subject_id: str, project_id: str, expected_revision: int | None = None, now: datetime | None = None) -> WaitRecord:
        record = self.get(wait_id, subject_id=subject_id, project_id=project_id)
        if record.state is not WaitState.CLAIMED:
            raise ValueError("only claimed waits can be completed")
        if expected_revision is not None and expected_revision != record.revision:
            raise ValueError("stale wait revision")
        now = _utc(now or datetime.now(UTC))
        if not record.schedule:
            with self._lock:
                cursor = self._db.execute("UPDATE waits SET state='completed', updated_at=?, revision=revision+1 WHERE wait_id=? AND state='claimed' AND revision=?", (now.isoformat(), wait_id, record.revision))
                if cursor.rowcount != 1:
                    raise ValueError("stale wait revision")
                self._event(wait_id, subject_id, project_id, "completed", now, {})
                return self.get(wait_id, subject_id=subject_id, project_id=project_id)
        if record.schedule.max_occurrences and record.occurrences + 1 >= record.schedule.max_occurrences:
            with self._lock:
                cursor = self._db.execute("UPDATE waits SET state='completed', updated_at=?, revision=revision+1, occurrences=occurrences+1 WHERE wait_id=? AND state='claimed' AND revision=?", (now.isoformat(), wait_id, record.revision))
                if cursor.rowcount != 1:
                    raise ValueError("stale wait revision")
                self._event(wait_id, subject_id, project_id, "completed", now, {"terminal": True})
                return self.get(wait_id, subject_id=subject_id, project_id=project_id)
        next_wake = _next_wake(record, now)
        if record.deadline and next_wake >= record.deadline:
            with self._lock:
                cursor = self._db.execute("UPDATE waits SET state='completed', updated_at=?, revision=revision+1, occurrences=occurrences+1 WHERE wait_id=? AND state='claimed' AND revision=?", (now.isoformat(), wait_id, record.revision))
                if cursor.rowcount != 1:
                    raise ValueError("stale wait revision")
                self._event(wait_id, subject_id, project_id, "completed", now, {"terminal": True, "deadline": True})
                return self.get(wait_id, subject_id=subject_id, project_id=project_id)
        with self._lock:
            cursor = self._db.execute("UPDATE waits SET state='waiting', wake_at=?, updated_at=?, occurrences=occurrences+1, revision=revision+1 WHERE wait_id=? AND state='claimed' AND revision=?", (next_wake.isoformat(), now.isoformat(), wait_id, record.revision))
            if cursor.rowcount != 1:
                raise ValueError("stale wait revision")
            self._event(wait_id, subject_id, project_id, "rescheduled", now, {"wake_at": next_wake.isoformat()})
            return self.get(wait_id, subject_id=subject_id, project_id=project_id)

    def wake(self, wait_id: str, *, subject_id: str, project_id: str, trigger: str, now: datetime | None = None) -> WaitRecord:
        trigger = _clean_trigger(trigger)
        if not trigger:
            raise ValueError("trigger is required")
        now = _utc(now or datetime.now(UTC))
        with self._lock:
            row = self._scoped_row(wait_id, subject_id, project_id)
            if row is None:
                raise KeyError(wait_id)
            if row["state"] != WaitState.WAITING.value:
                return _record(row)
            state, event = (WaitState.EXPIRED, "expired") if row["deadline"] and row["deadline"] <= now.isoformat() else (WaitState.READY, "woken")
            self._db.execute("UPDATE waits SET state=?, trigger=?, updated_at=?, revision=revision+1 WHERE wait_id=? AND state='waiting'", (state.value, trigger, now.isoformat(), wait_id))
            self._event(wait_id, subject_id, project_id, event, now, {"trigger": trigger})
            return self.get(wait_id, subject_id=subject_id, project_id=project_id)

    def cancel(self, wait_id: str, *, subject_id: str, project_id: str, reason: str = "", now: datetime | None = None) -> WaitRecord:
        now = _utc(now or datetime.now(UTC))
        reason = _clean_trigger(reason) or "cancelled"
        with self._lock:
            row = self._scoped_row(wait_id, subject_id, project_id)
            if row is None:
                raise KeyError(wait_id)
            if row["state"] in {WaitState.COMPLETED.value, WaitState.CANCELLED.value, WaitState.EXPIRED.value}:
                return _record(row)
            self._db.execute("UPDATE waits SET state='cancelled', updated_at=?, revision=revision+1 WHERE wait_id=? AND state IN ('waiting','ready','claimed')", (now.isoformat(), wait_id))
            self._event(wait_id, subject_id, project_id, "cancelled", now, {"reason": reason})
            return self.get(wait_id, subject_id=subject_id, project_id=project_id)

    def events(self, wait_id: str, *, subject_id: str, project_id: str) -> list[dict[str, object]]:
        self.get(wait_id, subject_id=subject_id, project_id=project_id)
        rows = self._db.execute("SELECT event_id,event,at,metadata_json FROM wait_events WHERE wait_id=? ORDER BY event_id", (wait_id,))
        return [{"event_id": r["event_id"], "event": r["event"], "at": r["at"], "metadata": json.loads(r["metadata_json"])} for r in rows]

    def _scoped_row(self, wait_id: str, subject_id: str, project_id: str) -> sqlite3.Row | None:
        return self._db.execute("SELECT * FROM waits WHERE wait_id=? AND subject_id=? AND project_id=?", (wait_id, subject_id, project_id)).fetchone()

    def _event(self, wait_id: str, subject_id: str, project_id: str, event: str, at: datetime, metadata: dict[str, object]) -> None:
        self._db.execute("INSERT INTO wait_events(wait_id,subject_id,project_id,event,at,metadata_json) VALUES(?,?,?,?,?,?)", (wait_id, subject_id, project_id, event, at.isoformat(), json.dumps(metadata, sort_keys=True, separators=(",", ":"))))


def _record(row: sqlite3.Row) -> WaitRecord:
    schedule = None
    if row["schedule_json"]:
        data = json.loads(row["schedule_json"])
        schedule = ScheduleSpec(kind=WaitKind(data["kind"]), interval_seconds=data.get("interval_seconds"), cron=data.get("cron"), max_occurrences=data.get("max_occurrences"))
    return WaitRecord(wait_id=row["wait_id"], subject_id=row["subject_id"], project_id=row["project_id"], kind=WaitKind(row["kind"]), state=WaitState(row["state"]), wake_at=_parse(row["wake_at"]), created_at=_parse(row["created_at"]), updated_at=_parse(row["updated_at"]), deadline=_parse(row["deadline"]) if row["deadline"] else None, priority=row["priority"], created_sequence=row["created_sequence"], schedule=schedule, trigger=row["trigger"], payload=json.loads(row["payload_json"]), occurrences=row["occurrences"], revision=row["revision"])


def _next_wake(record: WaitRecord, now: datetime) -> datetime:
    schedule = record.schedule
    assert schedule is not None
    if schedule.kind is WaitKind.RECURRING:
        assert schedule.interval_seconds is not None
        return max(record.wake_at + timedelta(seconds=schedule.interval_seconds), now)
    assert schedule.cron is not None
    candidate = record.wake_at.replace(second=0, microsecond=0) + timedelta(minutes=1)
    while not _cron_matches(schedule.cron, candidate):
        candidate += timedelta(minutes=1)
        if candidate - now > timedelta(days=366):
            raise ValueError("cron schedule has no occurrence within one year")
    return candidate


def _validate_cron(expression: str) -> None:
    fields = expression.split()
    ranges = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 6)]
    for field, bounds in zip(fields, ranges):
        for token in field.split(","):
            if token == "*":
                continue
            if token.startswith("*/"):
                step = int(token[2:])
                if step < 1 or step > bounds[1] - bounds[0] + 1:
                    raise ValueError("invalid cron step")
                continue
            if "-" in token:
                left, right = token.split("-", 1)
                if not bounds[0] <= int(left) <= int(right) <= bounds[1]:
                    raise ValueError("invalid cron range")
            elif not bounds[0] <= int(token) <= bounds[1]:
                raise ValueError("invalid cron value")


def _cron_matches(expression: str, value: datetime) -> bool:
    fields = expression.split()
    values = [value.minute, value.hour, value.day, value.month, (value.weekday() + 1) % 7]
    bounds = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 6)]
    for field, current, bound in zip(fields, values, bounds):
        allowed: set[int] = set()
        for token in field.split(","):
            if token == "*":
                allowed.update(range(bound[0], bound[1] + 1))
            elif token.startswith("*/"):
                allowed.update(range(bound[0], bound[1] + 1, int(token[2:])))
            elif "-" in token:
                left, right = map(int, token.split("-", 1))
                allowed.update(range(left, right + 1))
            else:
                allowed.add(int(token))
        if current not in allowed:
            return False
    return True


def _schedule_json(schedule: ScheduleSpec | None) -> str | None:
    if not schedule:
        return None
    return json.dumps({"kind": schedule.kind.value, "interval_seconds": schedule.interval_seconds, "cron": schedule.cron, "max_occurrences": schedule.max_occurrences}, sort_keys=True, separators=(",", ":"))


def _safe_payload(payload: dict[str, object]) -> dict[str, object]:
    secret_terms = ("password", "passwd", "secret", "api_key", "private_key", "credential", "access_token", "refresh_token", "bearer")
    def clean(value: object, key: str = "") -> object:
        if any(term in key.lower() for term in secret_terms):
            raise ValueError("secret-like wait field is not allowed")
        if isinstance(value, dict):
            return {str(k): clean(v, str(k)) for k, v in value.items()}
        if isinstance(value, list):
            return [clean(v, key) for v in value]
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        raise TypeError("wait payload must be JSON-safe")
    cleaned = clean(payload)
    encoded = json.dumps(cleaned, sort_keys=True, separators=(",", ":"))
    if len(encoded.encode("utf-8")) > _MAX_PAYLOAD:
        raise ValueError("wait payload exceeds 16 KiB")
    return cleaned  # type: ignore[return-value]


def _identity(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 512:
        raise ValueError(f"{name} is required")
    return value.strip()


def _clean_trigger(value: str | None) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("trigger must be a string")
    value = value.strip()
    if len(value) > 512:
        raise ValueError("trigger is too long")
    return value or None


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ValueError("datetime must be timezone-aware")
    return value.astimezone(UTC)


def _parse(value: str) -> datetime:
    return datetime.fromisoformat(value).astimezone(UTC)
