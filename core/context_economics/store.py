from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path
from tempfile import NamedTemporaryFile

from .models import ContextItem, ContextSelection


class ContextSnapshotStore:
    """Atomic JSON snapshots of context decisions for recovery and provenance."""

    schema_version = 1

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    @staticmethod
    def _item(item: ContextItem) -> dict[str, object]:
        payload = asdict(item)
        payload["scope"] = item.scope.value
        return payload

    def save(self, selection: ContextSelection) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": self.schema_version,
            "decision_id": selection.decision_id,
            "reason": selection.reason,
            "evidence": list(selection.evidence),
            "total_tokens": selection.total_tokens,
            "estimated_cost": selection.estimated_cost,
            "redacted": selection.redacted,
            "selected": [self._item(item) for item in selection.selected],
            "dropped": [self._item(item) for item in selection.dropped],
        }
        encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
        with NamedTemporaryFile(
            "w", encoding="utf-8", dir=self.path.parent, delete=False
        ) as temp:
            temp.write(encoded)
            temp.flush()
            os.fsync(temp.fileno())
            temporary = Path(temp.name)
        try:
            os.replace(temporary, self.path)
        finally:
            temporary.unlink(missing_ok=True)

    def load(self) -> dict[str, object] | None:
        if not self.path.exists():
            return None
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or payload.get("schema_version") != self.schema_version:
            raise ValueError("Unsupported context snapshot schema")
        return payload
