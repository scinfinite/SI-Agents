"""Persistent session authority for V4 Phase 53.

Sessions are durable SI Core state. This module deliberately does not restore or grant
capabilities, credentials, provider authorization, or identity: those remain governed by
existing authorization/runtime boundaries on every resumed operation.
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any, Mapping

_MAX_JSON_BYTES = 512 * 1024
_MAX_TEXT_BYTES = 256 * 1024
_SECRET_KEY = re.compile(r"(?:password|passwd|secret|token|api[_-]?key|private[_-]?key|credential)", re.I)


class SessionState(StrEnum):
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"
    EXPIRED = "expired"
    CLOSED = "closed"


@dataclass(frozen=True)
class SessionOwner:
    subject_id: str
    project_id: str
    workspace_id: str | None = None

    def validate(self) -> None:
        if not self.subject_id.strip() or not self.project_id.strip():
            raise ValueError("session owner requires subject_id and project_id")
        if self.workspace_id is not None and not self.workspace_id.strip():
            raise ValueError("workspace_id cannot be empty")


@dataclass(frozen=True)
class PersistentSession:
    session_id: str
    owner: SessionOwner
    harness_id: str
    state: SessionState = SessionState.ACTIVE
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    expires_at: float | None = None
    parent_session_id: str | None = None
    branch_name: str | None = None
    revision: int = 0

    def validate(self) -> None:
        if not self.session_id.strip() or not self.harness_id.strip():
            raise ValueError("session_id and harness_id are required")
        self.owner.validate()
        if self.revision < 0:
            raise ValueError("revision cannot be negative")
        if self.expires_at is not None and self.expires_at <= 0:
            raise ValueError("expires_at must be an epoch timestamp")


@dataclass(frozen=True)
class SessionEvent:
    event_id: str
    session_id: str
    sequence: int
    kind: str
    payload: Mapping[str, Any]
    occurred_at: float


@dataclass(frozen=True)
class SessionArtifact:
    artifact_id: str
    session_id: str
    kind: str
    name: str
    digest: str
    metadata: Mapping[str, Any]
    created_at: float


@dataclass(frozen=True)
class SessionExport:
    schema_version: str
    session: PersistentSession
    state: Mapping[str, Any]
    events: tuple[SessionEvent, ...]
    artifacts: tuple[SessionArtifact, ...]


class SessionStore:
    """SQLite-backed session authority with optimistic revisions and isolated access."""

    SCHEMA_VERSION = "si.session.v1"

    def __init__(self, path: str | Path = ":memory:") -> None:
        self.path = str(path)
        self._db = sqlite3.connect(self.path, check_same_thread=False, isolation_level=None)
        self._db.row_factory = sqlite3.Row
        self._lock = threading.RLock()
        self._db.execute("PRAGMA foreign_keys=ON")
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.executescript(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY, subject_id TEXT NOT NULL, project_id TEXT NOT NULL,
                workspace_id TEXT, harness_id TEXT NOT NULL, state TEXT NOT NULL,
                created_at REAL NOT NULL, updated_at REAL NOT NULL, expires_at REAL,
                parent_session_id TEXT REFERENCES sessions(session_id), branch_name TEXT,
                revision INTEGER NOT NULL DEFAULT 0
            );
            CREATE INDEX IF NOT EXISTS ix_sessions_owner ON sessions(subject_id, project_id);
            CREATE INDEX IF NOT EXISTS ix_sessions_state ON sessions(state);
            CREATE TABLE IF NOT EXISTS session_state (
                session_id TEXT PRIMARY KEY REFERENCES sessions(session_id) ON DELETE CASCADE,
                state_json TEXT NOT NULL, token_cost_json TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS session_events (
                event_id TEXT PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
                sequence INTEGER NOT NULL, kind TEXT NOT NULL, payload_json TEXT NOT NULL,
                occurred_at REAL NOT NULL, UNIQUE(session_id, sequence)
            );
            CREATE TABLE IF NOT EXISTS session_artifacts (
                artifact_id TEXT PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
                kind TEXT NOT NULL, name TEXT NOT NULL, digest TEXT NOT NULL, metadata_json TEXT NOT NULL,
                created_at REAL NOT NULL
            );
            CREATE INDEX IF NOT EXISTS ix_artifacts_session ON session_artifacts(session_id, created_at);
            """
        )

    def close(self) -> None:
        with self._lock:
            self._db.close()

    @staticmethod
    def _json(value: Any, *, max_bytes: int = _MAX_JSON_BYTES) -> str:
        encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        if len(encoded.encode("utf-8")) > max_bytes:
            raise ValueError("serialized session value exceeds safety limit")
        return encoded

    @staticmethod
    def _reject_secrets(value: Any, path: str = "state") -> None:
        if isinstance(value, Mapping):
            for key, child in value.items():
                key_text = str(key)
                if _SECRET_KEY.search(key_text):
                    raise ValueError(f"secret-like field rejected: {path}.{key_text}")
                SessionStore._reject_secrets(child, f"{path}.{key_text}")
        elif isinstance(value, (list, tuple)):
            for index, child in enumerate(value):
                SessionStore._reject_secrets(child, f"{path}[{index}]")

    def create(self, session: PersistentSession, *, state: Mapping[str, Any] | None = None) -> PersistentSession:
        session.validate()
        state = dict(state or {})
        self._reject_secrets(state)
        encoded = self._json(state)
        with self._lock:
            try:
                self._db.execute("BEGIN IMMEDIATE")
                self._db.execute(
                    "INSERT INTO sessions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (session.session_id, session.owner.subject_id, session.owner.project_id, session.owner.workspace_id,
                     session.harness_id, session.state.value, session.created_at, session.updated_at,
                     session.expires_at, session.parent_session_id, session.branch_name, session.revision),
                )
                self._db.execute("INSERT INTO session_state VALUES (?, ?, ?)", (session.session_id, encoded, "{}"))
                self._db.execute("COMMIT")
            except Exception:
                self._db.execute("ROLLBACK")
                raise
        return session

    def get(self, session_id: str, *, subject_id: str, project_id: str) -> PersistentSession:
        with self._lock:
            row = self._db.execute("SELECT * FROM sessions WHERE session_id=? AND subject_id=? AND project_id=?", (session_id, subject_id, project_id)).fetchone()
        if row is None:
            raise KeyError("session not found")
        return self._from_row(row)

    @staticmethod
    def _from_row(row: sqlite3.Row) -> PersistentSession:
        return PersistentSession(
            row["session_id"],
            SessionOwner(row["subject_id"], row["project_id"], row["workspace_id"]),
            row["harness_id"], SessionState(row["state"]), row["created_at"], row["updated_at"],
            row["expires_at"], row["parent_session_id"], row["branch_name"], row["revision"],
        )

    def _require(self, session_id: str, subject_id: str, project_id: str) -> sqlite3.Row:
        row = self._db.execute("SELECT * FROM sessions WHERE session_id=?", (session_id,)).fetchone()
        if row is None:
            raise KeyError("session not found")
        if row["subject_id"] != subject_id or row["project_id"] != project_id:
            raise PermissionError("session isolation mismatch")
        return row

    def update_state(
        self, session_id: str, *, subject_id: str, project_id: str, state: SessionState,
        expected_revision: int | None = None, patch: Mapping[str, Any] | None = None,
    ) -> PersistentSession:
        patch = dict(patch or {})
        self._reject_secrets(patch)
        self._json(patch)
        with self._lock:
            row = self._require(session_id, subject_id, project_id)
            if expected_revision is not None and row["revision"] != expected_revision:
                raise ValueError("session revision conflict")
            if row["state"] == SessionState.ARCHIVED.value and state is not SessionState.ARCHIVED:
                raise ValueError("archived session is immutable")
            now = time.time()
            new_revision = row["revision"] + 1
            self._db.execute("UPDATE sessions SET state=?, updated_at=?, revision=? WHERE session_id=?", (state.value, now, new_revision, session_id))
            if patch:
                current = json.loads(self._db.execute("SELECT state_json FROM session_state WHERE session_id=?", (session_id,)).fetchone()[0])
                current.update(patch)
                self._db.execute("UPDATE session_state SET state_json=? WHERE session_id=?", (self._json(current), session_id))
            return self.get(session_id, subject_id=subject_id, project_id=project_id)

    def set_context(
        self, session_id: str, *, subject_id: str, project_id: str,
        context: Mapping[str, Any], token_usage: Mapping[str, Any] | None = None,
        expected_revision: int | None = None,
    ) -> PersistentSession:
        self._reject_secrets(context, "context")
        self._reject_secrets(token_usage or {}, "token_usage")
        context_json, cost_json = self._json(context), self._json(token_usage or {})
        with self._lock:
            row = self._require(session_id, subject_id, project_id)
            if expected_revision is not None and row["revision"] != expected_revision:
                raise ValueError("session revision conflict")
            now, revision = time.time(), row["revision"] + 1
            self._db.execute("UPDATE session_state SET state_json=?, token_cost_json=? WHERE session_id=?", (context_json, cost_json, session_id))
            self._db.execute("UPDATE sessions SET updated_at=?, revision=? WHERE session_id=?", (now, revision, session_id))
        return self.get(session_id, subject_id=subject_id, project_id=project_id)

    def read_state(self, session_id: str, *, subject_id: str, project_id: str) -> dict[str, Any]:
        self.get(session_id, subject_id=subject_id, project_id=project_id)
        with self._lock:
            row = self._db.execute("SELECT state_json, token_cost_json FROM session_state WHERE session_id=?", (session_id,)).fetchone()
        return {"state": json.loads(row["state_json"]), "token_cost": json.loads(row["token_cost_json"])}

    def append_event(self, session_id: str, *, subject_id: str, project_id: str, kind: str, payload: Mapping[str, Any]) -> SessionEvent:
        if not kind or len(kind) > 128:
            raise ValueError("invalid session event kind")
        self._reject_secrets(payload, "event")
        encoded = self._json(payload, max_bytes=_MAX_JSON_BYTES)
        with self._lock:
            self._require(session_id, subject_id, project_id)
            row = self._db.execute("SELECT COALESCE(MAX(sequence), 0) + 1 AS next FROM session_events WHERE session_id=?", (session_id,)).fetchone()
            sequence = int(row["next"])
            event = SessionEvent(uuid.uuid4().hex, session_id, sequence, kind, dict(payload), time.time())
            self._db.execute("INSERT INTO session_events VALUES (?, ?, ?, ?, ?, ?)", (event.event_id, session_id, sequence, kind, encoded, event.occurred_at))
        return event

    def events(self, session_id: str, *, subject_id: str, project_id: str, after: int = 0, limit: int = 1000) -> tuple[SessionEvent, ...]:
        if after < 0 or limit < 1 or limit > 1000:
            raise ValueError("invalid event pagination")
        self.get(session_id, subject_id=subject_id, project_id=project_id)
        with self._lock:
            rows = self._db.execute("SELECT * FROM session_events WHERE session_id=? AND sequence>? ORDER BY sequence LIMIT ?", (session_id, after, limit)).fetchall()
        return tuple(SessionEvent(r["event_id"], r["session_id"], r["sequence"], r["kind"], json.loads(r["payload_json"]), r["occurred_at"]) for r in rows)

    def add_artifact(self, session_id: str, *, subject_id: str, project_id: str, kind: str, name: str, content: bytes, metadata: Mapping[str, Any] | None = None) -> SessionArtifact:
        if not kind.strip() or not name.strip():
            raise ValueError("artifact kind and name are required")
        if len(content) > _MAX_TEXT_BYTES:
            raise ValueError("artifact exceeds safety limit")
        self._reject_secrets(metadata or {}, "artifact.metadata")
        digest = hashlib.sha256(content).hexdigest()
        artifact = SessionArtifact(uuid.uuid4().hex, session_id, kind, name, digest, dict(metadata or {}), time.time())
        self.get(session_id, subject_id=subject_id, project_id=project_id)
        with self._lock:
            self._db.execute("INSERT INTO session_artifacts VALUES (?, ?, ?, ?, ?, ?, ?)", (artifact.artifact_id, session_id, kind, name, digest, self._json(artifact.metadata), artifact.created_at))
        return artifact

    def artifacts(self, session_id: str, *, subject_id: str, project_id: str) -> tuple[SessionArtifact, ...]:
        self.get(session_id, subject_id=subject_id, project_id=project_id)
        with self._lock:
            rows = self._db.execute("SELECT * FROM session_artifacts WHERE session_id=? ORDER BY created_at, artifact_id", (session_id,)).fetchall()
        return tuple(SessionArtifact(r["artifact_id"], r["session_id"], r["kind"], r["name"], r["digest"], json.loads(r["metadata_json"]), r["created_at"]) for r in rows)

    def list(self, *, subject_id: str, project_id: str, state: SessionState | None = None, harness_id: str | None = None, limit: int = 100) -> tuple[PersistentSession, ...]:
        if limit < 1 or limit > 1000:
            raise ValueError("invalid session limit")
        query = "SELECT * FROM sessions WHERE subject_id=? AND project_id=?"
        params: list[Any] = [subject_id, project_id]
        if state is not None:
            query += " AND state=?"; params.append(state.value)
        if harness_id is not None:
            query += " AND harness_id=?"; params.append(harness_id)
        query += " ORDER BY updated_at DESC, session_id LIMIT ?"; params.append(limit)
        with self._lock:
            rows = self._db.execute(query, params).fetchall()
        return tuple(self._from_row(row) for row in rows)

    def expire_due(self, *, now: float | None = None) -> tuple[PersistentSession, ...]:
        now = time.time() if now is None else now
        with self._lock:
            rows = self._db.execute("SELECT * FROM sessions WHERE expires_at IS NOT NULL AND expires_at<=? AND state IN (?, ?)", (now, SessionState.ACTIVE.value, SessionState.PAUSED.value)).fetchall()
            self._db.execute("UPDATE sessions SET state=?, updated_at=?, revision=revision+1 WHERE expires_at IS NOT NULL AND expires_at<=? AND state IN (?, ?)", (SessionState.EXPIRED.value, now, now, SessionState.ACTIVE.value, SessionState.PAUSED.value))
        return tuple(self._from_row(row) for row in rows)

    def archive(self, session_id: str, *, subject_id: str, project_id: str, expected_revision: int | None = None) -> PersistentSession:
        return self.update_state(session_id, subject_id=subject_id, project_id=project_id, state=SessionState.ARCHIVED, expected_revision=expected_revision)

    def export(self, session_id: str, *, subject_id: str, project_id: str) -> SessionExport:
        session = self.get(session_id, subject_id=subject_id, project_id=project_id)
        state = self.read_state(session_id, subject_id=subject_id, project_id=project_id)
        return SessionExport(self.SCHEMA_VERSION, session, state, self.events(session_id, subject_id=subject_id, project_id=project_id), self.artifacts(session_id, subject_id=subject_id, project_id=project_id))

    def import_session(self, bundle: SessionExport, *, subject_id: str, project_id: str, new_session_id: str | None = None) -> PersistentSession:
        if bundle.schema_version != self.SCHEMA_VERSION:
            raise ValueError("unsupported session export schema")
        if bundle.session.owner.subject_id != subject_id or bundle.session.owner.project_id != project_id:
            raise PermissionError("session import ownership mismatch")
        sid = new_session_id or uuid.uuid4().hex
        if not sid.strip():
            raise ValueError("new session id is required")
        original = bundle.session
        session = PersistentSession(sid, original.owner, original.harness_id, SessionState.ACTIVE, time.time(), time.time(), original.expires_at, original.parent_session_id, original.branch_name, 0)
        state = bundle.state.get("state", {})
        self.create(session, state=state)
        for event in bundle.events:
            self.append_event(sid, subject_id=subject_id, project_id=project_id, kind=event.kind, payload=event.payload)
        return session

    def clone(self, session_id: str, *, subject_id: str, project_id: str, branch_name: str, new_session_id: str | None = None) -> PersistentSession:
        if not branch_name.strip() or len(branch_name) > 128:
            raise ValueError("invalid branch name")
        bundle = self.export(session_id, subject_id=subject_id, project_id=project_id)
        sid = new_session_id or uuid.uuid4().hex
        state = bundle.state.get("state", {})
        clone = PersistentSession(sid, bundle.session.owner, bundle.session.harness_id, SessionState.ACTIVE, time.time(), time.time(), bundle.session.expires_at, bundle.session.session_id, branch_name, 0)
        self.create(clone, state=state)
        self.append_event(sid, subject_id=subject_id, project_id=project_id, kind="session.cloned", payload={"parent_session_id": bundle.session.session_id, "branch_name": branch_name})
        return clone

    def search(self, *, subject_id: str, project_id: str, text: str, limit: int = 50) -> tuple[PersistentSession, ...]:
        text = text.strip()
        if not text:
            raise ValueError("search text is required")
        if len(text.encode("utf-8")) > 256:
            raise ValueError("search text is too long")
        pattern = f"%{text}%"
        with self._lock:
            rows = self._db.execute("SELECT DISTINCT s.* FROM sessions s LEFT JOIN session_events e ON e.session_id=s.session_id WHERE s.subject_id=? AND s.project_id=? AND (s.session_id LIKE ? OR s.harness_id LIKE ? OR e.kind LIKE ? OR e.payload_json LIKE ?) ORDER BY s.updated_at DESC LIMIT ?", (subject_id, project_id, pattern, pattern, pattern, pattern, limit)).fetchall()
        return tuple(self._from_row(row) for row in rows)

    def replay(self, session_id: str, *, subject_id: str, project_id: str, after: int = 0) -> tuple[SessionEvent, ...]:
        """Return the immutable event sequence; replay never mutates or re-authorizes work."""
        return self.events(session_id, subject_id=subject_id, project_id=project_id, after=after)

    def recover(self) -> tuple[PersistentSession, ...]:
        """Recover durable sessions without changing authority or inventing state."""
        return self.expire_due()
