from __future__ import annotations

from core.events.bus import EventBus
from core.events.models import Event, EventName, EventSource

from .models import KnowledgeEntry, MemoryEntry, MemoryScope, PromotionDecision
from .promotion import MemoryPromoter
from .registry import MemoryRegistry
from .retrieval import MemoryRetriever
from .store import MemoryStore


class MemoryService:
    """Coordinates memory lifecycle without becoming a permission authority."""

    def __init__(
        self,
        registry: MemoryRegistry | None = None,
        *,
        promoter: MemoryPromoter | None = None,
        store: MemoryStore | None = None,
        events: EventBus | None = None,
    ) -> None:
        self.registry = registry or MemoryRegistry()
        self.promoter = promoter or MemoryPromoter()
        self.store = store
        self.events = events
        self.retriever = MemoryRetriever(self.registry)

    def _publish(self, name: EventName, subject: str, payload: dict[str, object]) -> None:
        if self.events is not None:
            self.events.publish(Event(name.value, EventSource.RUNTIME, subject, payload))

    def record(self, entry: MemoryEntry) -> MemoryEntry:
        self.registry.add(entry)
        self._persist()
        self._publish(
            EventName.MEMORY_CREATED,
            entry.id,
            {"scope": entry.scope.value, "status": entry.status.value},
        )
        return entry

    def evaluate_promotion(
        self, memory_id: str, target_scope: MemoryScope | None = None
    ) -> PromotionDecision:
        return self.promoter.evaluate(self.registry.get(memory_id), target_scope)

    def promote(self, memory_id: str, target_scope: MemoryScope | None = None) -> MemoryEntry:
        current = self.registry.get(memory_id)
        promoted = self.promoter.promote(current, target_scope)
        self.registry.promote(current.id, promoted)
        self._persist()
        self._publish(
            EventName.MEMORY_PROMOTED,
            promoted.id,
            {"scope": promoted.scope.value, "version": promoted.version},
        )
        return promoted

    def add_knowledge(self, entry: KnowledgeEntry) -> KnowledgeEntry:
        self.registry.add_knowledge(entry)
        self._persist()
        self._publish(
            EventName.KNOWLEDGE_CREATED,
            entry.id,
            {"version": entry.version, "confidence": entry.confidence},
        )
        return entry

    def expire(self, memory_id: str) -> MemoryEntry:
        entry = self.registry.expire(memory_id)
        self._persist()
        self._publish(EventName.MEMORY_EXPIRED, entry.id, {"status": entry.status.value})
        return entry

    def reject(self, memory_id: str) -> MemoryEntry:
        entry = self.registry.reject(memory_id)
        self._persist()
        self._publish(EventName.MEMORY_REJECTED, entry.id, {"status": entry.status.value})
        return entry

    def _persist(self) -> None:
        if self.store is not None:
            self.store.save(self.registry)
