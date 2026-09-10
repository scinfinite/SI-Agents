from datetime import UTC, datetime, timedelta

import pytest

from core.memory import (
    MemoryEntry,
    MemoryEvidence,
    MemoryPromoter,
    MemoryRegistry,
    MemoryRetriever,
    MemoryScope,
    MemoryStatus,
    MemoryStore,
    MemoryType,
)


def evidence(verified=True, suffix="a"):
    return MemoryEvidence(f"source-{suffix}", f"verified observation {suffix}", verified=verified)


def make_memory(**kwargs):
    defaults = dict(
        content="Use contract tests before integration tests for service boundaries",
        memory_type=MemoryType.LESSON,
        scope=MemoryScope.TASK,
        task_id="task-1",
        project_id="project-1",
        provenance=("task-result",),
        evidence=(evidence(True), evidence(True, "b")),
        confidence=0.9,
        tags=("testing", "contracts"),
    )
    defaults.update(kwargs)
    return MemoryEntry(**defaults)


def test_scopes_require_anchors():
    with pytest.raises(ValueError):
        make_memory(scope=MemoryScope.PROJECT, project_id=None)
    with pytest.raises(ValueError):
        make_memory(scope=MemoryScope.TASK, task_id=None)


def test_promotion_is_fail_closed():
    promoter = MemoryPromoter()
    weak = make_memory(confidence=0.5, evidence=(evidence(False),))
    decision = promoter.evaluate(weak)
    assert not decision.allowed
    assert "Confidence" in " ".join(decision.reasons)
    assert "evidence" in " ".join(decision.reasons).lower()


def test_promotion_moves_only_one_scope_and_versions():
    promoted = MemoryPromoter().promote(make_memory())
    assert promoted.scope is MemoryScope.PROJECT
    assert promoted.status is MemoryStatus.PROMOTED
    assert promoted.version == 2
    assert not MemoryPromoter().evaluate(promoted, MemoryScope.GLOBAL).allowed


def test_registry_rejects_duplicates_and_tracks_supersession():
    registry = MemoryRegistry()
    first = make_memory()
    registry.add(first)
    with pytest.raises(ValueError):
        registry.add(first)
    replacement = make_memory(id="replacement", version=2, supersedes=first.id)
    registry.supersede(first.id, replacement)
    assert registry.get(first.id).status is MemoryStatus.EXPIRED
    assert registry.get("replacement").version == 2


def test_retrieval_respects_scope_project_and_tags():
    registry = MemoryRegistry()
    wanted = make_memory()
    registry.add(wanted)
    registry.add(make_memory(id="other", content="database migration rollback", tags=("database",)))
    found = MemoryRetriever(registry).search("contract testing", project_id="project-1", tags=("testing",))
    assert found == (wanted,)


def test_expired_memory_is_not_retrieved():
    registry = MemoryRegistry()
    now = datetime.now(UTC)
    expired = make_memory(created_at=now - timedelta(days=2), expires_at=now - timedelta(days=1))
    registry.add(expired)
    assert MemoryRetriever(registry).search("contract") == ()


def test_json_store_round_trip(tmp_path):
    registry = MemoryRegistry()
    entry = make_memory()
    registry.add(entry)
    path = tmp_path / "memory.json"
    MemoryStore(path).save(registry)
    restored = MemoryStore(path).load()
    loaded = restored.get(entry.id)
    assert loaded.content == entry.content
    assert loaded.evidence == entry.evidence
    assert loaded.created_at == entry.created_at


def test_store_rejects_non_list(tmp_path):
    path = tmp_path / "memory.json"
    path.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError):
        MemoryStore(path).load()
