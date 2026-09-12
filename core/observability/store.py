"""Durable, bounded telemetry storage with redaction and integrity checks."""
from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
import sqlite3
import time
import uuid
from pathlib import Path

from core.security.platform import SecretScanner

from .models import Severity, TelemetryRecord

MAX_PAYLOAD_BYTES = 64 * 1024
MAX_RECORDS_QUERY = 1000
MAX_RECORDS_INTEGRITY_SCAN = 100_000
_SECRET_KEYS = {"authorization", "api_key", "credential", "password", "private_key", "secret", "token"}


def _canon(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sanitize(value: object, depth: int = 0) -> object:
    if depth > 8:
        raise ValueError("telemetry nesting exceeds limit")
    if isinstance(value, Mapping):
        if len(value) > 256:
            raise ValueError("telemetry mapping exceeds limit")
        output: dict[str, object] = {}
        for key, item in value.items():
            if not isinstance(key, str) or not key.strip():
                raise TypeError("telemetry keys must be non-empty strings")
            normalized = key.strip().lower().replace("-", "_")
            output[key] = "[REDACTED]" if normalized in _SECRET_KEYS else _sanitize(item, depth + 1)
        return output
    if isinstance(value, (list, tuple)):
        if len(value) > 256:
            raise ValueError("telemetry list exceeds limit")
        return [_sanitize(item, depth + 1) for item in value]
    if isinstance(value, str):
        lowered = value.casefold()
        patterns = ("bearer ", "api_key=", "api-key=", "password=", "secret=", "token=", "credential=")
        return "[REDACTED]" if SecretScanner.contains_secret(value) or any(pattern in lowered for pattern in patterns) else value
    if value is None or isinstance(value, (int, float, bool)):
        return value
    raise TypeError(f"unsupported telemetry value: {type(value).__name__}")


def _envelope(record: TelemetryRecord) -> dict[str, object]:
    return {"record_id": record.record_id, "occurred_at": record.occurred_at, "kind": record.kind, "name": record.name, "severity": record.severity.value, "tenant_id": record.tenant_id, "project_id": record.project_id, "entity_type": record.entity_type, "entity_id": record.entity_id, "correlation_id": record.correlation_id, "causation_id": record.causation_id, "payload": record.payload}


class TelemetryStore:
    def __init__(self, path: str | Path = ":memory:") -> None:
        self.db = sqlite3.connect(str(path), isolation_level=None, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("""CREATE TABLE IF NOT EXISTS telemetry(
            record_id TEXT PRIMARY KEY, occurred_at REAL NOT NULL, kind TEXT NOT NULL,
            name TEXT NOT NULL, severity TEXT NOT NULL, tenant_id TEXT, project_id TEXT,
            entity_type TEXT, entity_id TEXT, correlation_id TEXT, causation_id TEXT,
            payload_json TEXT NOT NULL, digest TEXT NOT NULL)""")
        self.db.execute("CREATE INDEX IF NOT EXISTS ix_tel_time ON telemetry(occurred_at,record_id)")
        self.db.execute("CREATE INDEX IF NOT EXISTS ix_tel_scope ON telemetry(tenant_id,project_id,occurred_at)")

    def close(self) -> None:
        self.db.close()

    def append(self, *, kind: str, name: str, severity: Severity = Severity.INFO, tenant_id: str | None = None, project_id: str | None = None, entity_type: str | None = None, entity_id: str | None = None, correlation_id: str | None = None, causation_id: str | None = None, payload: Mapping[str, object] | None = None) -> TelemetryRecord:
        if not kind.strip() or not name.strip():
            raise ValueError("telemetry kind and name are required")
        safe = _sanitize(dict(payload or {}))
        encoded = _canon(safe)
        if len(encoded.encode("utf-8")) > MAX_PAYLOAD_BYTES:
            raise ValueError("telemetry payload exceeds limit")
        record_id = uuid.uuid4().hex
        occurred_at = time.time()
        value = severity.value if isinstance(severity, Severity) else str(severity)
        if value not in {item.value for item in Severity}:
            raise ValueError("invalid telemetry severity")
        envelope = {"record_id": record_id, "occurred_at": occurred_at, "kind": kind, "name": name, "severity": value, "tenant_id": tenant_id, "project_id": project_id, "entity_type": entity_type, "entity_id": entity_id, "correlation_id": correlation_id, "causation_id": causation_id, "payload": safe}
        digest = hashlib.sha256(_canon(envelope).encode("utf-8")).hexdigest()
        self.db.execute("INSERT INTO telemetry VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", (record_id, occurred_at, kind, name, value, tenant_id, project_id, entity_type, entity_id, correlation_id, causation_id, encoded, digest))
        return self.get(record_id)

    def get(self, record_id: str) -> TelemetryRecord:
        row = self.db.execute("SELECT * FROM telemetry WHERE record_id=?", (record_id,)).fetchone()
        if row is None:
            raise KeyError(record_id)
        return TelemetryRecord(row["record_id"], row["occurred_at"], row["kind"], row["name"], Severity(row["severity"]), row["tenant_id"], row["project_id"], row["entity_type"], row["entity_id"], row["correlation_id"], row["causation_id"], json.loads(row["payload_json"]), row["digest"])

    def query(self, *, tenant_id: str | None = None, project_id: str | None = None, kind: str | None = None, name: str | None = None, severity: Severity | str | None = None, correlation_id: str | None = None, limit: int = 100, offset: int = 0) -> tuple[TelemetryRecord, ...]:
        clauses: list[str] = []
        params: list[object] = []
        for column, value in (("tenant_id", tenant_id), ("project_id", project_id), ("kind", kind), ("name", name), ("severity", severity.value if isinstance(severity, Severity) else severity), ("correlation_id", correlation_id)):
            if value is not None:
                clauses.append(f"{column}=?")
                params.append(value)
        bounded_limit = max(1, min(limit, MAX_RECORDS_QUERY))
        bounded_offset = max(0, offset)
        sql = "SELECT * FROM telemetry" + ((" WHERE " + " AND ".join(clauses)) if clauses else "") + " ORDER BY occurred_at,record_id LIMIT ? OFFSET ?"
        rows = self.db.execute(sql, (*params, bounded_limit, bounded_offset)).fetchall()
        return tuple(self.get(row["record_id"]) for row in rows)

    def export_jsonl(self, *, tenant_id: str | None = None, project_id: str | None = None) -> str:
        records = self.query(tenant_id=tenant_id, project_id=project_id, limit=MAX_RECORDS_QUERY)
        lines = []
        for record in records:
            payload = {"record_id": record.record_id, "occurred_at": record.occurred_at, "kind": record.kind, "name": record.name, "severity": record.severity.value, "tenant_id": record.tenant_id, "project_id": record.project_id, "entity_type": record.entity_type, "entity_id": record.entity_id, "correlation_id": record.correlation_id, "causation_id": record.causation_id, "payload": record.payload, "digest": record.digest}
            lines.append(json.dumps(payload, sort_keys=True, separators=(",", ":")))
        return "".join(line + "\n" for line in lines)

    def integrity(self, *, tenant_id: str | None = None, project_id: str | None = None) -> bool:
        offset = 0
        checked = 0
        while checked < MAX_RECORDS_INTEGRITY_SCAN:
            batch = self.query(tenant_id=tenant_id, project_id=project_id, limit=MAX_RECORDS_QUERY, offset=offset)
            if not batch:
                return True
            for record in batch:
                if hashlib.sha256(_canon(_envelope(record)).encode("utf-8")).hexdigest() != record.digest:
                    return False
            checked += len(batch)
            offset += len(batch)
            if len(batch) < MAX_RECORDS_QUERY:
                return True
        return False
