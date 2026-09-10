from __future__ import annotations

import json
import os
from dataclasses import asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from tempfile import NamedTemporaryFile

from .models import KnowledgeEntry, MemoryEntry, MemoryEvidence, MemoryScope, MemoryStatus, MemoryType
from .registry import MemoryRegistry


class MemoryStore:
    """Dependency-free atomic JSON persistence for auditable memory and knowledge."""

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
        raise TypeError(f"Unsupported memory value: {type(value).__name__}")

    def save(self, registry: MemoryRegistry) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": 2,
            "memories": [asdict(entry) for entry in registry.list(include_expired=True)],
            "knowledge": [asdict(entry) for entry in registry.list_knowledge()],
        }
        encoded = json.dumps(payload, default=self._encode, indent=2, sort_keys=True) + "\n"
        with NamedTemporaryFile("w", encoding="utf-8", dir=self.path.parent, delete=False) as temp:
            temp.write(encoded)
            temp.flush()
            os.fsync(temp.fileno())
            temporary_path = Path(temp.name)
        os.replace(temporary_path, self.path)

    @staticmethod
    def _memory(raw: dict) -> MemoryEntry:
        raw = dict(raw)
        raw["evidence"] = tuple(MemoryEvidence(**item) for item in raw.get("evidence", ()))
        for key in ("created_at", "expires_at"):
            if raw.get(key):
                raw[key] = datetime.fromisoformat(raw[key])
        raw["memory_type"] = MemoryType(raw["memory_type"])
        raw["scope"] = MemoryScope(raw["scope"])
        raw["status"] = MemoryStatus(raw["status"])
        for key in ("tags", "provenance", "contradicts"):
            raw[key] = tuple(raw.get(key, ()))
        return MemoryEntry(**raw)

    @staticmethod
    def _knowledge(raw: dict) -> KnowledgeEntry:
        raw = dict(raw)
        raw["evidence"] = tuple(MemoryEvidence(**item) for item in raw.get("evidence", ()))
        if raw.get("created_at"):
            raw["created_at"] = datetime.fromisoformat(raw["created_at"])
        raw["tags"] = tuple(raw.get("tags", ()))
        return KnowledgeEntry(**raw)

    def load(self) -> MemoryRegistry:
        registry = MemoryRegistry()
        if not self.path.exists():
            return registry
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        if isinstance(payload, list):  # v1 compatibility
            for raw in payload:
                registry.add(self._memory(raw))
            return registry
        if not isinstance(payload, dict) or payload.get("schema_version") != 2:
            raise ValueError("Unsupported memory store schema")
        for raw in payload.get("memories", ()):
            registry.add(self._memory(raw))
        for raw in payload.get("knowledge", ()):
            registry.add_knowledge(self._knowledge(raw))
        return registry
