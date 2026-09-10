from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from enum import Enum
from pathlib import Path

from .models import MemoryEntry, MemoryEvidence, MemoryScope, MemoryStatus, MemoryType
from .registry import MemoryRegistry


class MemoryStore:
    """Small dependency-free JSON persistence layer for auditable memory."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    @staticmethod
    def _encode(value):
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, tuple):
            return list(value)
        return value

    def save(self, registry: MemoryRegistry) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [asdict(entry) for entry in registry.list(include_expired=True)]
        self.path.write_text(json.dumps(payload, default=self._encode, indent=2) + "\n", encoding="utf-8")

    def load(self) -> MemoryRegistry:
        registry = MemoryRegistry()
        if not self.path.exists():
            return registry
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError("Memory store must contain a JSON list")
        for raw in payload:
            evidence = tuple(MemoryEvidence(**item) for item in raw.pop("evidence", []))
            raw["evidence"] = evidence
            for key in ("created_at", "expires_at"):
                if raw.get(key):
                    raw[key] = datetime.fromisoformat(raw[key])
            raw["memory_type"] = MemoryType(raw["memory_type"])
            raw["scope"] = MemoryScope(raw["scope"])
            raw["status"] = MemoryStatus(raw["status"])
            raw["tags"] = tuple(raw.get("tags", ()))
            raw["provenance"] = tuple(raw.get("provenance", ()))
            registry.add(MemoryEntry(**raw))
        return registry
