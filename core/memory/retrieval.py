from __future__ import annotations

from .models import KnowledgeEntry, MemoryEntry, MemoryScope
from .registry import MemoryRegistry


class MemoryRetriever:
    """Deterministic scope-aware retrieval; ranking is not evidence or authorization."""

    def __init__(self, registry: MemoryRegistry) -> None:
        self.registry = registry

    def search(
        self,
        query: str,
        *,
        project_id: str | None = None,
        task_id: str | None = None,
        team_id: str | None = None,
        agent_id: str | None = None,
        division_id: str | None = None,
        organization_id: str | None = None,
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
        candidates: list[tuple[int, float, object, str, MemoryEntry]] = []
        for entry in self.registry.list(scope=scope):
            context = {
                "project": project_id,
                "task": task_id,
                "team": team_id,
                "agent": agent_id,
                "division": division_id,
                "organization": organization_id,
            }
            entry_context = {
                "project": entry.project_id,
                "task": entry.task_id,
                "team": entry.team_id,
                "agent": entry.agent_id,
                "division": entry.division_id,
                "organization": entry.organization_id,
            }
            if any(value is not None and entry_context[key] != value for key, value in context.items()):
                continue
            if required_tags and not required_tags.issubset({tag.lower() for tag in entry.tags}):
                continue
            haystack = f"{entry.content} {entry.memory_type.value} {' '.join(entry.tags)}".lower()
            score = sum(term in haystack for term in terms)
            if score:
                candidates.append((score, entry.confidence, entry.created_at, entry.id, entry))
        candidates.sort(key=lambda item: (item[0], item[1], item[2], item[3]), reverse=True)
        return tuple(item[4] for item in candidates[:limit])

    def search_knowledge(self, query: str, *, tags: tuple[str, ...] = (), limit: int = 10) -> tuple[KnowledgeEntry, ...]:
        if not query.strip():
            raise ValueError("Knowledge query must not be empty")
        if limit < 1:
            raise ValueError("limit must be positive")
        terms = {term.lower() for term in query.split() if term.strip()}
        required_tags = {tag.lower() for tag in tags}
        matches: list[tuple[int, float, object, str, KnowledgeEntry]] = []
        for entry in self.registry.list_knowledge():
            if required_tags and not required_tags.issubset({tag.lower() for tag in entry.tags}):
                continue
            haystack = f"{entry.subject} {entry.claim} {entry.source} {' '.join(entry.tags)}".lower()
            score = sum(term in haystack for term in terms)
            if score:
                matches.append((score, entry.confidence, entry.created_at, entry.id, entry))
        matches.sort(key=lambda item: (item[0], item[1], item[2], item[3]), reverse=True)
        return tuple(item[4] for item in matches[:limit])
