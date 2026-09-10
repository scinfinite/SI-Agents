from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

from .models import MemoryEntry, MemoryScope, MemoryStatus


class MemoryRegistry:
    """In-memory registry with explicit lifecycle and supersession semantics."""

    def __init__(self) -> None:
        self._entries: dict[str, MemoryEntry] = {}

    def add(self, entry: MemoryEntry) -> MemoryEntry:
        if entry.id in self._entries:
            raise ValueError(f"Memory entry already exists: {entry.id}")
        self._entries[entry.id] = entry
        return entry

    def get(self, memory_id: str) -> MemoryEntry:
        try:
            return self._entries[memory_id]
        except KeyError as exc:
            raise KeyError(f"Unknown memory entry: {memory_id}") from exc

    def list(self, scope: MemoryScope | None = None, include_expired: bool = False) -> tuple[MemoryEntry, ...]:
        now = datetime.now(UTC)
        entries = tuple(self._entries.values())
        if scope is not None:
            entries = tuple(e for e in entries if e.scope is scope)
        if not include_expired:
            entries = tuple(e for e in entries if not e.is_expired(now) and e.status is not MemoryStatus.EXPIRED)
        return entries

    def supersede(self, memory_id: str, replacement: MemoryEntry) -> MemoryEntry:
        current = self.get(memory_id)
        if replacement.supersedes != current.id:
            raise ValueError("Replacement must explicitly supersede the current memory")
        if replacement.version <= current.version:
            raise ValueError("Replacement version must be greater than current version")
        self._entries[replacement.id] = replacement
        self._entries[current.id] = replace(current, status=MemoryStatus.EXPIRED)
        return replacement

    def expire(self, memory_id: str) -> MemoryEntry:
        current = self.get(memory_id)
        updated = replace(current, status=MemoryStatus.EXPIRED)
        self._entries[memory_id] = updated
        return updated

    def reject(self, memory_id: str) -> MemoryEntry:
        current = self.get(memory_id)
        updated = replace(current, status=MemoryStatus.REJECTED)
        self._entries[memory_id] = updated
        return updated
