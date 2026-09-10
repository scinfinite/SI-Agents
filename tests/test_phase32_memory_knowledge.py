from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from core.events.bus import EventBus
from core.events.models import EventName
from core.memory import (
    KnowledgeEntry,
    MemoryEntry,
    MemoryEvidence,
    MemoryPromoter,
    MemoryRegistry,
    MemoryRetriever,
    MemoryScope,
    MemoryService,
    MemoryStatus,
    MemoryStore,
    MemoryType,
)


def evidence(*, verified: bool = True, claim: str = "claim") -> MemoryEvidence:
    return MemoryEvidence("test:evidence", claim, verified=verified, evidence_id="ev-1")


def memory(**kwargs) -> MemoryEntry:
    return MemoryEntry(
        content=kwargs.pop("content", "Use deterministic tests"),
        memory_type=kwargs.pop("memory_type", MemoryType.LESSON),
        scope=kwargs.pop("scope", MemoryScope.TASK),
        task_id=kwargs.pop("task_id", "task-1"),
        project_id=kwargs.pop("project_id", "project-1"),
        provenance=kwargs.pop("provenance", ("run:1",)),
        evidence=kwargs.pop("evidence", (evidence(), evidence(claim="independent claim"))),
        confidence=kwargs.pop("confidence", 0.95),
        **kwargs,
    )


def test_scope_requires_matching_identifier() -> None:
    with pytest.raises(ValueError, match="project_id"):
        MemoryEntry("x", MemoryType.FACT, MemoryScope.PROJECT, provenance=("run:1",))


def test_expired_memory_is_not_retrieved() -> None:
    entry = memory(expires_at=datetime.now(UTC) - timedelta(seconds=1))
    registry = MemoryRegistry()
    registry.add(entry)
    assert registry.list() == ()
    assert registry.list(include_expired=True) == (entry,)


def test_retrieval_is_context_scoped_and_deterministic() -> None:
    registry = MemoryRegistry()
    first = memory(id="a", content="deploy safely")
    second = memory(id="b", content="deploy safely", project_id="other")
    registry.add(first)
    registry.add(second)
    results = MemoryRetriever(registry).search("deploy", project_id="project-1")
    assert results == (first,)


def test_promotion_requires_verified_evidence_and_confidence() -> None:
    promoter = MemoryPromoter(minimum_confidence=0.9, minimum_verified_evidence=2)
    entry = memory()
    decision = promoter.evaluate(entry, MemoryScope.PROJECT)
    assert decision.allowed
    promoted = promoter.promote(entry, MemoryScope.PROJECT)
    assert promoted.status is MemoryStatus.PROMOTED
    assert promoted.scope is MemoryScope.PROJECT
    assert promoted.version == 2


def test_promotion_fails_closed_for_unverified_evidence() -> None:
    entry = memory(evidence=(evidence(verified=False), evidence(verified=False)))
    decision = MemoryPromoter().evaluate(entry, MemoryScope.PROJECT)
    assert not decision.allowed
    assert "Insufficient verified evidence" in decision.reasons


def test_promotion_cannot_skip_scope() -> None:
    entry = memory()
    decision = MemoryPromoter().evaluate(entry, MemoryScope.GLOBAL)
    assert not decision.allowed
    assert "one scope at a time" in decision.reasons[0]


def test_supersession_requires_explicit_link_and_higher_version() -> None:
    registry = MemoryRegistry()
    current = memory(id="old")
    replacement = memory(id="new", supersedes="old", version=2, content="new rule")
    registry.add(current)
    registry.supersede("old", replacement)
    assert registry.get("old").status is MemoryStatus.EXPIRED
    assert registry.get("new") == replacement
    with pytest.raises(ValueError, match="supersede"):
        registry.supersede("new", memory(id="bad", version=3))


def test_knowledge_requires_verified_evidence() -> None:
    with pytest.raises(ValueError, match="verified evidence"):
        KnowledgeEntry("python", "3.13", "docs", evidence=(evidence(verified=False),))
    item = KnowledgeEntry("python", "3.13", "docs", evidence=(evidence(),), confidence=0.99)
    registry = MemoryRegistry()
    registry.add_knowledge(item)
    assert MemoryRetriever(registry).search_knowledge("python") == (item,)


def test_store_round_trip_preserves_memory_knowledge_and_timestamps(tmp_path) -> None:
    registry = MemoryRegistry()
    item = memory()
    knowledge = KnowledgeEntry("python", "3.13", "docs", evidence=(evidence(),), confidence=0.99)
    registry.add(item)
    registry.add_knowledge(knowledge)
    path = tmp_path / "memory.json"
    MemoryStore(path).save(registry)
    restored = MemoryStore(path).load()
    assert restored.get(item.id) == item
    assert restored.get_knowledge(knowledge.id) == knowledge


def test_store_rejects_unknown_schema(tmp_path) -> None:
    path = tmp_path / "memory.json"
    path.write_text('{"schema_version": 999}', encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported memory store schema"):
        MemoryStore(path).load()


def test_memory_service_publishes_lifecycle_events() -> None:
    registry = MemoryRegistry()
    bus = EventBus()
    service = MemoryService(registry, events=bus)
    entry = memory()
    service.record(entry)
    promoted = service.promote(entry.id, MemoryScope.PROJECT)
    assert promoted.status is MemoryStatus.PROMOTED
    journal = bus.store.all()
    assert [event.name for event in journal] == [
        EventName.MEMORY_CREATED.value,
        EventName.MEMORY_PROMOTED.value,
    ]
