from __future__ import annotations

from .models import MemoryEntry, MemoryScope
from .registry import MemoryRegistry


class MemoryRetriever:
    """Deterministic, scope-aware retrieval; no semantic proof is implied by ranking."""

    def __init__(self, registry: MemoryRegistry) -> None:
        self.registry = registry

    def search(
        self,
        query: str,
        *,
        project_id: str | None = None,
        task_id: str | None = None,
        scope: MemoryScope | None = None,
        tags: tuple[str, ...] = (),
        limit: int = 10,
    ) -> tuple[MemoryEntry, ...]:
        if not query.strip():
            raise ValueError("Memory query must not be empty")
        if limit < 1:
            raise ValueError("limit must be positive")
        terms = {term.lower() for term in query.split() if term.strip()}
        required_tags = {tag.lower() for tag in tags}
        candidates = []
        for entry in self.registry.list(scope=scope):
            if project_id is not None and entry.project_id != project_id:
                continue
            if task_id is not None and entry.task_id != task_id:
                continue
            if required_tags and not required_tags.issubset({tag.lower() for tag in entry.tags}):
                continue
            haystack = f"{entry.content} {entry.memory_type.value} {' '.join(entry.tags)}".lower()
            score = sum(term in haystack for term in terms)
            if score:
                candidates.append((score, entry.confidence, entry.created_at, entry))
        candidates.sort(key=lambda item: (item[0], item[1], item[2]), reverse=True)
        return tuple(item[3] for item in candidates[:limit])
