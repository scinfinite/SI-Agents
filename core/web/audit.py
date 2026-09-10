"""Redacted mutation audit logging for the Web surface."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any


_SENSITIVE = re.compile(r"(token|secret|password|credential|authorization|api[_-]?key|private[_-]?key)", re.IGNORECASE)


def redact(value: Any, *, depth: int = 0) -> Any:
    """Return JSON-safe metadata with secret-like keys and values removed."""
    if depth > 6:
        return "<redacted-depth>"
    if isinstance(value, dict):
        return {str(key): "<redacted>" if _SENSITIVE.search(str(key)) else redact(item, depth=depth + 1) for key, item in value.items()}
    if isinstance(value, list):
        return [redact(item, depth=depth + 1) for item in value[:100]]
    if isinstance(value, tuple):
        return [redact(item, depth=depth + 1) for item in value[:100]]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return "<redacted>"


class AuditLogger:
    """Append-only local JSONL audit sink; never logs request bodies verbatim."""

    def __init__(self, path: Path) -> None:
        self.path = path.expanduser()
        self._lock = Lock()

    def record(self, *, request_id: str, method: str, path: str, status: int, metadata: dict[str, Any] | None = None) -> None:
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": request_id[:128],
            "method": method,
            "path": path[:512],
            "status": status,
            "metadata": redact(metadata or {}),
        }
        payload = json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n"
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
            old_umask = os.umask(0o077)
            try:
                fd = os.open(self.path, flags, 0o600)
            finally:
                os.umask(old_umask)
            try:
                os.write(fd, payload.encode("utf-8"))
            finally:
                os.close(fd)
            try:
                self.path.chmod(0o600)
            except OSError:
                pass
