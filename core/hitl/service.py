"""Fail-closed human-in-the-loop approval authority for SI Core V4 Phase 54."""
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
_TERMINAL = {ApprovalState.APPROVED, ApprovalState.REJECTED, ApprovalState.MODIFIED, ApprovalState.RETRY, ApprovalState.REASSIGNED, ApprovalState.ALTERNATIVE, ApprovalState.EXPIRED, ApprovalState.CANCELLED}


def _bounded_json(value: Any) -> str:
    try:
        encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    except (TypeError, ValueError) as exc:
        raise ValueError("approval value must be JSON serializable") from exc
    if len(encoded.encode("utf-8")) > _MAX_JSON_BYTES:
        raise ValueError("approval value exceeds safety limit")
    return encoded


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} is required")
    if len(value) > _MAX_TEXT:
        raise ValueError(f"{field} exceeds {_MAX_TEXT} characters")
    return value.strip()


def _reject_secret_keys(value: Any, path: str = "payload") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key).lower().replace("-", "_")
            if any(token in key_text for token in ("password", "passwd", "secret", "api_key", "private_key", "credential", "access_token", "auth_token", "refresh_token", "bearer")):
                raise ValueError(f"secret-like field rejected: {path}.{key}")
            _reject_secret_keys(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_secret_keys(child, f"{path}[{index}]")


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
    state: ApprovalState = ApprovalState.PENDING
    risk: str = "low"
    estimated_cost: float = 0.0
    external_egress: bool = False
    destructive: bool = False
    security_sensitive: bool = False
    deployment: bool = False
    session_id: str | None = None
    run_id: str | None = None
    revision: int = 0
    decision_by: str | None = None
    decision_at: float | None = None
    decision_reason: str | None = None
    decision_payload: Mapping[str, Any] = None  # type: ignore[assignment]
    evidence_digest: str = ""

    def as_dict(self) -> dict[str, object]:
        return {"approval_id": self.approval_id, "subject_id": self.subject_id, "project_id": self.project_id, "kind": self.kind, "gate": self.gate, "action": self.action, "summary": self.summary, "requested_by": self.requested_by, "requested_at": self.requested_at, "expires_at": self.expires_at, "state": self.state.value, "risk": self.risk, "estimated_cost": self.estimated_cost, "external_egress": self.external_egress, "destructive": self.destructive, "security_sensitive": self.security_sensitive, "deployment": self.deployment, "session_id": self.session_id, "run_id": self.run_id, "revision": self.revision, "decision_by": self.decision_by, "decision_at": self.decision_at, "decision_reason": self.decision_reason, "decision_payload": dict(self.decision_payload or {}), "evidence_digest": self.evidence_digest}


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
    """Durable approval authority; every mutation is identity/project bound and fail-closed."""

    SCHEMA_VERSION = "si.hitl.v1"

    def __init__(self, path: str | Path = ":memory:") -> None:
        self.path = str(path)
        self._db = sqlite3.connect(self.path, check_same_thread=False, isolation_level=None)
        self._db.row_factory = sqlite3.Row
        self._lock = threading.RLock()
        self._db.execute("PRAGMA foreign_keys=ON")
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.executescript("""
            CREATE TABLE IF NOT EXISTS approvals (
                approval_id TEXT PRIMARY KEY, subject_id TEXT NOT NULL, project_id TEXT NOT NULL,
                kind TEXT NOT NULL, gate TEXT NOT NULL, action TEXT NOT NULL, summary TEXT NOT NULL,
                requested_by TEXT NOT NULL, requested_at REAL NOT NULL, expires_at REAL NOT NULL,
                state TEXT NOT NULL, risk TEXT NOT NULL, estimated_cost REAL NOT NULL,
                external_egress INTEGER NOT NULL, destructive INTEGER NOT NULL, security_sensitive INTEGER NOT NULL,
                deployment INTEGER NOT NULL, session_id TEXT, run_id TEXT, revision INTEGER NOT NULL,
                decision_by TEXT, decision_at REAL, decision_reason TEXT, decision_payload TEXT NOT NULL,
                evidence_digest TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS ix_approvals_queue ON approvals(project_id, subject_id, state, expires_at);
            CREATE INDEX IF NOT EXISTS ix_approvals_run ON approvals(run_id);
            CREATE TABLE IF NOT EXISTS approval_events (
                event_id TEXT PRIMARY KEY, approval_id TEXT NOT NULL REFERENCES approvals(approval_id) ON DELETE CASCADE,
                sequence INTEGER NOT NULL, state TEXT NOT NULL, actor TEXT NOT NULL, occurred_at REAL NOT NULL,
                payload_json TEXT NOT NULL, evidence_digest TEXT NOT NULL, UNIQUE(approval_id, sequence)
            );
        """)

    def close(self) -> None:
        with self._lock:
            self._db.close()

    @staticmethod
    def _row(row: sqlite3.Row) -> ApprovalRequest:
        return ApprovalRequest(row["approval_id"], row["subject_id"], row["project_id"], row["kind"], row["gate"], row["action"], row["summary"], row["requested_by"], row["requested_at"], row["expires_at"], ApprovalState(row["state"]), row["risk"], row["estimated_cost"], bool(row["external_egress"]), bool(row["destructive"]), bool(row["security_sensitive"]), bool(row["deployment"]), row["session_id"], row["run_id"], row["revision"], row["decision_by"], row["decision_at"], row["decision_reason"], json.loads(row["decision_payload"]), row["evidence_digest"])

    def _require(self, approval_id: str, subject_id: str, project_id: str) -> sqlite3.Row:
        row = self._db.execute("SELECT * FROM approvals WHERE approval_id=?", (approval_id,)).fetchone()
        if row is None:
            raise KeyError("approval not found")
        if row["subject_id"] != subject_id or row["project_id"] != project_id:
            raise PermissionError("approval isolation mismatch")
        if row["state"] == ApprovalState.PENDING.value and row["expires_at"] <= time.time():
            self._expire_locked(approval_id, "system")
            row = self._db.execute("SELECT * FROM approvals WHERE approval_id=?", (approval_id,)).fetchone()
        return row

    def _expire_locked(self, approval_id: str, actor: str) -> None:
        row = self._db.execute("SELECT * FROM approvals WHERE approval_id=?", (approval_id,)).fetchone()
        if row is None or row["state"] != ApprovalState.PENDING.value:
            return
        now = time.time()
        digest = hashlib.sha256(f"{approval_id}|expired|{actor}|{now:.6f}".encode()).hexdigest()
        self._db.execute("UPDATE approvals SET state=?, decision_by=?, decision_at=?, decision_reason=?, revision=revision+1, evidence_digest=? WHERE approval_id=?", (ApprovalState.EXPIRED.value, actor, now, "approval expired", digest, approval_id))
        seq = self._db.execute("SELECT COALESCE(MAX(sequence),0)+1 FROM approval_events WHERE approval_id=?", (approval_id,)).fetchone()[0]
        self._db.execute("INSERT INTO approval_events VALUES (?,?,?,?,?,?,?)", (uuid.uuid4().hex, approval_id, seq, ApprovalState.EXPIRED.value, actor, now, "{}", digest))

    def create(self, payload: Mapping[str, Any]) -> ApprovalRequest:
        _reject_secret_keys(payload)
        subject_id, project_id = _text(payload.get("subject_id"), "subject_id"), _text(payload.get("project_id"), "project_id")
        requested_by = _text(payload.get("requested_by"), "requested_by")
        if requested_by != subject_id and not bool(payload.get("allow_delegate", False)):
            raise PermissionError("requester identity is not bound to subject")
        kind, gate, action, summary = (_text(payload.get(k), k) for k in ("kind", "gate", "action", "summary"))
        if kind not in _ALLOWED_KINDS or gate not in _ALLOWED_GATES:
            raise ValueError("unsupported approval kind or gate")
        try:
            estimated_cost = float(payload.get("estimated_cost", 0.0))
            expires_in = float(payload.get("expires_in", 3600.0))
        except (TypeError, ValueError) as exc:
            raise ValueError("estimated_cost and expires_in must be numbers") from exc
        if estimated_cost < 0 or expires_in <= 0 or expires_in > 7 * 24 * 3600:
            raise ValueError("invalid cost or expiry window")
        decision_payload = payload.get("metadata", {})
        if not isinstance(decision_payload, Mapping):
            raise TypeError("metadata must be an object")
        _bounded_json(decision_payload)
        now = time.time()
        approval_id = f"approval_{uuid.uuid4().hex}"
        digest = hashlib.sha256(_bounded_json({"approval_id": approval_id, "subject_id": subject_id, "project_id": project_id, "action": action, "gate": gate, "risk": payload.get("risk", "low"), "estimated_cost": estimated_cost, "external_egress": bool(payload.get("external_egress", False)), "destructive": bool(payload.get("destructive", False)), "deployment": bool(payload.get("deployment", False))}).encode()).hexdigest()
        with self._lock:
            count = self._db.execute("SELECT COUNT(*) FROM approvals WHERE project_id=? AND state=?", (project_id, ApprovalState.PENDING.value)).fetchone()[0]
            if count >= _MAX_QUEUE:
                raise ValueError("approval queue limit reached")
            self._db.execute("INSERT INTO approvals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (approval_id, subject_id, project_id, kind, gate, action, summary, requested_by, now, now + expires_in, ApprovalState.PENDING.value, str(payload.get("risk", "low")), estimated_cost, int(bool(payload.get("external_egress", False))), int(bool(payload.get("destructive", False))), int(bool(payload.get("security_sensitive", False))), int(bool(payload.get("deployment", False))), payload.get("session_id"), payload.get("run_id"), 0, None, None, None, _bounded_json(decision_payload), digest))
            self._db.execute("INSERT INTO approval_events VALUES (?,?,?,?,?,?,?)", (uuid.uuid4().hex, approval_id, 1, ApprovalState.PENDING.value, requested_by, now, _bounded_json({"notification": "queued"}), digest))
            return self._row(self._db.execute("SELECT * FROM approvals WHERE approval_id=?", (approval_id,)).fetchone())

    def get(self, approval_id: str, *, subject_id: str, project_id: str) -> ApprovalRequest:
        with self._lock:
            return self._row(self._require(approval_id, subject_id, project_id))

    def queue(self, *, subject_id: str, project_id: str, state: ApprovalState | None = ApprovalState.PENDING, limit: int = 100) -> list[ApprovalRequest]:
        if limit < 1 or limit > 100:
            raise ValueError("limit must be between 1 and 100")
        with self._lock:
            if state is ApprovalState.PENDING:
                rows = self._db.execute("SELECT * FROM approvals WHERE subject_id=? AND project_id=? AND state=? ORDER BY requested_at, approval_id LIMIT ?", (subject_id, project_id, state.value, limit)).fetchall()
                for row in rows:
                    if row["expires_at"] <= time.time():
                        self._expire_locked(row["approval_id"], "system")
                rows = self._db.execute("SELECT * FROM approvals WHERE subject_id=? AND project_id=? AND state=? ORDER BY requested_at, approval_id LIMIT ?", (subject_id, project_id, state.value, limit)).fetchall()
            else:
                rows = self._db.execute("SELECT * FROM approvals WHERE subject_id=? AND project_id=? AND state=? ORDER BY requested_at DESC, approval_id LIMIT ?", (subject_id, project_id, state.value if state else ApprovalState.PENDING.value, limit)).fetchall()
            return [self._row(row) for row in rows]

    def decide(self, approval_id: str, *, subject_id: str, project_id: str, decision: ApprovalState, decision_by: str, reason: str, payload: Mapping[str, Any] | None = None, expected_revision: int | None = None) -> ApprovalDecision:
        if decision not in _TERMINAL - {ApprovalState.EXPIRED, ApprovalState.CANCELLED}:
            raise ValueError("invalid terminal decision")
        decision_by, reason = _text(decision_by, "decision_by"), _text(reason, "reason")
        if not isinstance(payload or {}, Mapping):
            raise TypeError("decision payload must be an object")
        _reject_secret_keys(payload or {}, "decision")
        encoded = _bounded_json(payload or {})
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
            self._db.execute("INSERT INTO approval_events VALUES (?,?,?,?,?,?,?)", (uuid.uuid4().hex, approval_id, revision + 1, decision.value, decision_by, now, encoded, digest))
            return ApprovalDecision(approval_id, decision, decision_by, reason, dict(payload or {}), digest)

    def cancel(self, approval_id: str, *, subject_id: str, project_id: str, actor: str, reason: str = "cancelled") -> ApprovalDecision:
        return self.decide(approval_id, subject_id=subject_id, project_id=project_id, decision=ApprovalState.CANCELLED, decision_by=actor, reason=reason)

    def events(self, approval_id: str, *, subject_id: str, project_id: str) -> list[dict[str, object]]:
        with self._lock:
            self._require(approval_id, subject_id, project_id)
            rows = self._db.execute("SELECT * FROM approval_events WHERE approval_id=? ORDER BY sequence", (approval_id,)).fetchall()
            return [{"event_id": row["event_id"], "approval_id": approval_id, "sequence": row["sequence"], "state": row["state"], "actor": row["actor"], "occurred_at": row["occurred_at"], "payload": json.loads(row["payload_json"]), "evidence_digest": row["evidence_digest"]} for row in rows]
