from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

from .models import KnowledgeEntry, MemoryEntry, MemoryScope, MemoryStatus


class MemoryRegistry:
    """In-process memory registry with explicit lifecycle and supersession semantics."""

    def __init__(self) -> None:
        self._entries: dict[str, MemoryEntry] = {}
        self._knowledge: dict[str, KnowledgeEntry] = {}

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
        return tuple(sorted(entries, key=lambda entry: (entry.created_at, entry.id), reverse=True))

    def promote(self, current_id: str, promoted: MemoryEntry) -> MemoryEntry:
        current = self.get(current_id)
        if promoted.id == current.id:
            raise ValueError("Promoted memory must have a new id")
        if promoted.supersedes != current.id:
            raise ValueError("Promoted memory must supersede its current version")
        if promoted.version <= current.version:
            raise ValueError("Promoted memory version must be greater than current version")
        self._entries[promoted.id] = promoted
        self._entries[current.id] = replace(current, status=MemoryStatus.EXPIRED)
        return promoted

    def supersede(self, memory_id: str, replacement: MemoryEntry) -> MemoryEntry:
        return self.promote(memory_id, replacement)

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

    def add_knowledge(self, entry: KnowledgeEntry) -> KnowledgeEntry:
        if entry.id in self._knowledge:
            raise ValueError(f"Knowledge entry already exists: {entry.id}")
        self._knowledge[entry.id] = entry
        return entry

    def get_knowledge(self, knowledge_id: str) -> KnowledgeEntry:
        try:
            return self._knowledge[knowledge_id]
        except KeyError as exc:
            raise KeyError(f"Unknown knowledge entry: {knowledge_id}") from exc

    def list_knowledge(self) -> tuple[KnowledgeEntry, ...]:
        return tuple(sorted(self._knowledge.values(), key=lambda entry: (entry.created_at, entry.id), reverse=True))

    def supersede_knowledge(self, knowledge_id: str, replacement: KnowledgeEntry) -> KnowledgeEntry:
        current = self.get_knowledge(knowledge_id)
        if replacement.supersedes != current.id:
            raise ValueError("Replacement must explicitly supersede current knowledge")
        if replacement.version <= current.version:
            raise ValueError("Replacement version must be greater than current knowledge")
        self._knowledge[replacement.id] = replacement
        return replacement
