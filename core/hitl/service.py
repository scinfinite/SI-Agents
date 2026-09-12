"""Fail-closed durable human-in-the-loop approval authority."""
from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import time
import uuid
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, Mapping

_MAX_JSON_BYTES = 256 * 1024
_MAX_TEXT = 512
_MAX_QUEUE = 1000


class ApprovalState(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"
    RETRY = "retry"
    REASSIGNED = "reassigned"
    ALTERNATIVE = "alternative"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


_ALLOWED_KINDS = {"approval", "input", "review"}
_ALLOWED_GATES = {"risk", "cost", "egress", "destructive", "security", "deployment", "human_input", "review"}
_DECISIONS = {ApprovalState.APPROVED, ApprovalState.REJECTED, ApprovalState.MODIFIED, ApprovalState.RETRY, ApprovalState.REASSIGNED, ApprovalState.ALTERNATIVE, ApprovalState.CANCELLED}


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} is required")
    if len(value) > _MAX_TEXT:
        raise ValueError(f"{field} exceeds {_MAX_TEXT} characters")
    return value.strip()


def _json(value: Any) -> str:
    try:
        encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    except (TypeError, ValueError) as exc:
        raise ValueError("approval value must be JSON serializable") from exc
    if len(encoded.encode("utf-8")) > _MAX_JSON_BYTES:
        raise ValueError("approval value exceeds safety limit")
    return encoded


def _reject_secrets(value: Any, path: str = "payload") -> None:
    if isinstance(value, Mapping):
        tokens = ("password", "passwd", "secret", "api_key", "private_key", "credential", "access_token", "auth_token", "refresh_token", "bearer")
        for key, child in value.items():
            normalized = str(key).lower().replace("-", "_")
            if any(token in normalized for token in tokens):
                raise ValueError(f"secret-like field rejected: {path}.{key}")
            _reject_secrets(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_secrets(child, f"{path}[{index}]")


@dataclass(frozen=True)
class ApprovalRequest:
    approval_id: str
    subject_id: str
    project_id: str
    kind: str
    gate: str
    action: str
    summary: str
    requested_by: str
    requested_at: float
    expires_at: float
    state: ApprovalState
    risk: str
    estimated_cost: float
    external_egress: bool
    destructive: bool
    security_sensitive: bool
    deployment: bool
    session_id: str | None
    run_id: str | None
    revision: int
    decision_by: str | None
    decision_at: float | None
    decision_reason: str | None
    decision_payload: Mapping[str, Any]
    evidence_digest: str

    def as_dict(self) -> dict[str, object]:
        return {"approval_id": self.approval_id, "subject_id": self.subject_id, "project_id": self.project_id, "kind": self.kind, "gate": self.gate, "action": self.action, "summary": self.summary, "requested_by": self.requested_by, "requested_at": self.requested_at, "expires_at": self.expires_at, "state": self.state.value, "risk": self.risk, "estimated_cost": self.estimated_cost, "external_egress": self.external_egress, "destructive": self.destructive, "security_sensitive": self.security_sensitive, "deployment": self.deployment, "session_id": self.session_id, "run_id": self.run_id, "revision": self.revision, "decision_by": self.decision_by, "decision_at": self.decision_at, "decision_reason": self.decision_reason, "decision_payload": dict(self.decision_payload), "evidence_digest": self.evidence_digest}


@dataclass(frozen=True)
class ApprovalDecision:
    approval_id: str
    state: ApprovalState
    decision_by: str
    reason: str
    payload: Mapping[str, Any]
    evidence_digest: str

    def as_dict(self) -> dict[str, object]:
        return {"approval_id": self.approval_id, "state": self.state.value, "decision_by": self.decision_by, "reason": self.reason, "payload": dict(self.payload), "evidence_digest": self.evidence_digest}


class HumanApprovalService:
    """Persistent HITL state; decisions never grant execution authority."""

    SCHEMA_VERSION = "si.hitl.v1"

    def __init__(self, path: str | Path = ":memory:") -> None:
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(self.path, check_same_thread=False, isolation_level=None)
        self._db.row_factory = sqlite3.Row
        self._lock = threading.RLock()
        self._db.execute("PRAGMA foreign_keys=ON")
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.executescript(
            """
            CREATE TABLE IF NOT EXISTS approvals (
                approval_id TEXT PRIMARY KEY, subject_id TEXT NOT NULL, project_id TEXT NOT NULL,
                kind TEXT NOT NULL, gate TEXT NOT NULL, action TEXT NOT NULL, summary TEXT NOT NULL,
                requested_by TEXT NOT NULL, requested_at REAL NOT NULL, expires_at REAL NOT NULL,
                state TEXT NOT NULL, risk TEXT NOT NULL, estimated_cost REAL NOT NULL,
                external_egress INTEGER NOT NULL, destructive INTEGER NOT NULL,
                security_sensitive INTEGER NOT NULL, deployment INTEGER NOT NULL,
                session_id TEXT, run_id TEXT, revision INTEGER NOT NULL,
                decision_by TEXT, decision_at REAL, decision_reason TEXT,
                decision_payload TEXT NOT NULL, evidence_digest TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS ix_approvals_queue ON approvals(project_id, subject_id, state, expires_at);
            CREATE INDEX IF NOT EXISTS ix_approvals_run ON approvals(run_id);
            CREATE TABLE IF NOT EXISTS approval_events (
                event_id TEXT PRIMARY KEY, approval_id TEXT NOT NULL REFERENCES approvals(approval_id) ON DELETE CASCADE,
                sequence INTEGER NOT NULL, state TEXT NOT NULL, actor TEXT NOT NULL,
                occurred_at REAL NOT NULL, payload_json TEXT NOT NULL,
                evidence_digest TEXT NOT NULL, UNIQUE(approval_id, sequence)
            );
            """
        )

    def close(self) -> None:
        with self._lock:
            self._db.close()

    def _row(self, row: sqlite3.Row) -> ApprovalRequest:
        return ApprovalRequest(approval_id=row["approval_id"], subject_id=row["subject_id"], project_id=row["project_id"], kind=row["kind"], gate=row["gate"], action=row["action"], summary=row["summary"], requested_by=row["requested_by"], requested_at=row["requested_at"], expires_at=row["expires_at"], state=ApprovalState(row["state"]), risk=row["risk"], estimated_cost=row["estimated_cost"], external_egress=bool(row["external_egress"]), destructive=bool(row["destructive"]), security_sensitive=bool(row["security_sensitive"]), deployment=bool(row["deployment"]), session_id=row["session_id"], run_id=row["run_id"], revision=row["revision"], decision_by=row["decision_by"], decision_at=row["decision_at"], decision_reason=row["decision_reason"], decision_payload=json.loads(row["decision_payload"]), evidence_digest=row["evidence_digest"])

    def _expire_locked(self, approval_id: str) -> None:
        row = self._db.execute("SELECT * FROM approvals WHERE approval_id=?", (approval_id,)).fetchone()
        if row is None or row["state"] != ApprovalState.PENDING.value:
            return
        now = time.time()
        digest = hashlib.sha256(f"{approval_id}|expired|{now:.6f}".encode()).hexdigest()
        self._db.execute("UPDATE approvals SET state=?, decision_by=?, decision_at=?, decision_reason=?, revision=revision+1, evidence_digest=? WHERE approval_id=?", (ApprovalState.EXPIRED.value, "system", now, "approval expired", digest, approval_id))
        sequence = self._db.execute("SELECT COALESCE(MAX(sequence), 0) + 1 FROM approval_events WHERE approval_id=?", (approval_id,)).fetchone()[0]
        self._db.execute("INSERT INTO approval_events VALUES (?,?,?,?,?,?,?,?)", (uuid.uuid4().hex, approval_id, sequence, ApprovalState.EXPIRED.value, "system", now, "{}", digest))

    def _require(self, approval_id: str, subject_id: str, project_id: str) -> sqlite3.Row:
        row = self._db.execute("SELECT * FROM approvals WHERE approval_id=?", (approval_id,)).fetchone()
        if row is None:
            raise KeyError("approval not found")
        if row["subject_id"] != subject_id or row["project_id"] != project_id:
            raise PermissionError("approval isolation mismatch")
        if row["state"] == ApprovalState.PENDING.value and row["expires_at"] <= time.time():
            self._expire_locked(approval_id)
            row = self._db.execute("SELECT * FROM approvals WHERE approval_id=?", (approval_id,)).fetchone()
        return row

    def create(self, payload: Mapping[str, Any]) -> ApprovalRequest:
        _reject_secrets(payload)
        subject_id = _text(payload.get("subject_id"), "subject_id")
        project_id = _text(payload.get("project_id"), "project_id")
        requested_by = _text(payload.get("requested_by"), "requested_by")
        if requested_by != subject_id:
            raise PermissionError("requester identity is not bound to subject")
        kind = _text(payload.get("kind"), "kind")
        gate = _text(payload.get("gate"), "gate")
        action = _text(payload.get("action"), "action")
        summary = _text(payload.get("summary"), "summary")
        if kind not in _ALLOWED_KINDS or gate not in _ALLOWED_GATES:
            raise ValueError("unsupported approval kind or gate")
        try:
            estimated_cost = float(payload.get("estimated_cost", 0.0))
            expires_in = float(payload.get("expires_in", 3600.0))
        except (TypeError, ValueError) as exc:
            raise ValueError("estimated_cost and expires_in must be numbers") from exc
        if estimated_cost < 0 or not 0 < expires_in <= 7 * 24 * 3600:
            raise ValueError("invalid cost or expiry window")
        metadata = payload.get("metadata", {})
        if not isinstance(metadata, Mapping):
            raise TypeError("metadata must be an object")
        metadata_json = _json(metadata)
        now = time.time()
        approval_id = f"approval_{uuid.uuid4().hex}"
        fingerprint = _json({"approval_id": approval_id, "subject_id": subject_id, "project_id": project_id, "action": action, "gate": gate, "risk": payload.get("risk", "low"), "estimated_cost": estimated_cost})
        digest = hashlib.sha256(fingerprint.encode()).hexdigest()
        values = (approval_id, subject_id, project_id, kind, gate, action, summary, requested_by, now, now + expires_in, ApprovalState.PENDING.value, str(payload.get("risk", "low")), estimated_cost, int(bool(payload.get("external_egress", False))), int(bool(payload.get("destructive", False))), int(bool(payload.get("security_sensitive", False))), int(bool(payload.get("deployment", False))), payload.get("session_id"), payload.get("run_id"), 0, None, None, None, metadata_json, digest)
        with self._lock:
            count = self._db.execute("SELECT COUNT(*) FROM approvals WHERE project_id=? AND state=?", (project_id, ApprovalState.PENDING.value)).fetchone()[0]
            if count >= _MAX_QUEUE:
                raise ValueError("approval queue limit reached")
            self._db.execute("INSERT INTO approvals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", values)
            self._db.execute("INSERT INTO approval_events VALUES (?,?,?,?,?,?,?,?)", (uuid.uuid4().hex, approval_id, 1, ApprovalState.PENDING.value, requested_by, now, '{"notification":"queued"}', digest))
            return self._row(self._db.execute("SELECT * FROM approvals WHERE approval_id=?", (approval_id,)).fetchone())

    def get(self, approval_id: str, *, subject_id: str, project_id: str) -> ApprovalRequest:
        with self._lock:
            return self._row(self._require(approval_id, subject_id, project_id))

    def queue(self, *, subject_id: str, project_id: str, state: ApprovalState = ApprovalState.PENDING, limit: int = 100) -> list[ApprovalRequest]:
        if not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100")
        with self._lock:
            rows = self._db.execute("SELECT * FROM approvals WHERE subject_id=? AND project_id=? AND state=? ORDER BY requested_at, approval_id LIMIT ?", (subject_id, project_id, state.value, limit)).fetchall()
            if state is ApprovalState.PENDING:
                for row in rows:
                    if row["expires_at"] <= time.time():
                        self._expire_locked(row["approval_id"])
                rows = self._db.execute("SELECT * FROM approvals WHERE subject_id=? AND project_id=? AND state=? ORDER BY requested_at, approval_id LIMIT ?", (subject_id, project_id, state.value, limit)).fetchall()
            return [self._row(row) for row in rows]

    def decide(self, approval_id: str, *, subject_id: str, project_id: str, decision: ApprovalState, decision_by: str, reason: str, payload: Mapping[str, Any] | None = None, expected_revision: int | None = None) -> ApprovalDecision:
        if decision not in _DECISIONS:
            raise ValueError("invalid terminal decision")
        decision_by = _text(decision_by, "decision_by")
        reason = _text(reason, "reason")
        decision_payload = payload or {}
        if not isinstance(decision_payload, Mapping):
            raise TypeError("decision payload must be an object")
        _reject_secrets(decision_payload, "decision")
        encoded = _json(decision_payload)
        with self._lock:
            row = self._require(approval_id, subject_id, project_id)
            if row["state"] != ApprovalState.PENDING.value:
                raise ValueError("approval is no longer pending")
            if expected_revision is not None and row["revision"] != expected_revision:
                raise ValueError("approval revision conflict")
            now = time.time()
            digest = hashlib.sha256(f"{row['evidence_digest']}|{decision.value}|{decision_by}|{reason}|{encoded}".encode()).hexdigest()
            revision = row["revision"] + 1
            self._db.execute("UPDATE approvals SET state=?, decision_by=?, decision_at=?, decision_reason=?, decision_payload=?, revision=?, evidence_digest=? WHERE approval_id=?", (decision.value, decision_by, now, reason, encoded, revision, digest, approval_id))
            self._db.execute("INSERT INTO approval_events VALUES (?,?,?,?,?,?,?,?)", (uuid.uuid4().hex, approval_id, revision + 1, decision.value, decision_by, now, encoded, digest))
            return ApprovalDecision(approval_id, decision, decision_by, reason, dict(decision_payload), digest)

    def cancel(self, approval_id: str, *, subject_id: str, project_id: str, actor: str, reason: str = "cancelled") -> ApprovalDecision:
        return self.decide(approval_id, subject_id=subject_id, project_id=project_id, decision=ApprovalState.CANCELLED, decision_by=actor, reason=reason)

    def events(self, approval_id: str, *, subject_id: str, project_id: str) -> list[dict[str, object]]:
        with self._lock:
            self._require(approval_id, subject_id, project_id)
            rows = self._db.execute("SELECT * FROM approval_events WHERE approval_id=? ORDER BY sequence", (approval_id,)).fetchall()
            return [{"event_id": row["event_id"], "approval_id": approval_id, "sequence": row["sequence"], "state": row["state"], "actor": row["actor"], "occurred_at": row["occurred_at"], "payload": json.loads(row["payload_json"]), "evidence_digest": row["evidence_digest"]} for row in rows]
