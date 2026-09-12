from pathlib import Path

import pytest

from core.context_economics import (
    ContextBudget,
    ContextEconomics,
    ContextItem,
    ContextScope,
    ContextSnapshotStore,
    ModelContextProfile,
)


MODEL = ModelContextProfile(
    "test-model",
    context_window_tokens=100,
    reserved_output_tokens=20,
    input_token_cost=0.01,
)


def item(
    item_id: str,
    content: str,
    *,
    importance: float = 0.5,
    relevance: float = 0.5,
    sensitive: bool = False,
    secret_like: bool = False,
) -> ContextItem:
    return ContextItem(
        item_id,
        content,
        ContextScope.TASK,
        importance,
        relevance,
        provenance=("test",),
        sensitive=sensitive,
        secret_like=secret_like,
    )


def test_model_capacity_and_budget_are_fail_closed() -> None:
    with pytest.raises(ValueError):
        ModelContextProfile("x", 10, 10)
    with pytest.raises(ValueError):
        ContextBudget(ContextScope.TASK, 0)
    with pytest.raises(ValueError):
        ContextEconomics(
            (
                ContextBudget(ContextScope.TASK, 10),
                ContextBudget(ContextScope.TASK, 20),
            )
        )


def test_selection_is_deterministic_and_budgeted() -> None:
    engine = ContextEconomics((ContextBudget(ContextScope.TASK, 12),))
    inputs = (
        item("low", "low", importance=0.1),
        item("high", "high", importance=0.9),
        item("mid", "mid", importance=0.5),
    )
    first = engine.select(inputs, MODEL, active_scopes=(ContextScope.TASK,))
    second = engine.select(tuple(reversed(inputs)), MODEL, active_scopes=(ContextScope.TASK,))
    assert first.decision_id == second.decision_id
    assert first.total_tokens <= 12
    assert first.selected == second.selected


def test_duplicate_content_is_not_double_counted() -> None:
    engine = ContextEconomics()
    result = engine.select((item("a", "same words"), item("b", "same words")), MODEL)
    assert len(result.selected) == 1
    assert result.total_tokens == result.selected[0].token_estimate()


def test_sensitive_context_is_excluded_without_permission() -> None:
    engine = ContextEconomics()
    secret = item("s", "private", sensitive=True)
    result = engine.select((secret,), MODEL)
    assert not result.selected
    assert result.dropped == (secret,)
    permitted = engine.select((secret,), MODEL, allow_sensitive=True)
    assert permitted.selected == (secret,)


def test_secret_like_context_is_redacted() -> None:
    engine = ContextEconomics()
    secret = item("s", "Authorization: Bearer abc123", secret_like=True)
    result = engine.select((secret,), MODEL)
    assert result.redacted
    assert "abc123" not in result.selected[0].content
    assert "REDACTED" in result.selected[0].content


def test_secret_like_context_can_be_dropped_instead_of_redacted() -> None:
    engine = ContextEconomics()
    secret = item("s", "Authorization: Bearer abc123", secret_like=True)
    result = engine.select((secret,), MODEL, redact_secrets=False)
    assert not result.selected


def test_compaction_preserves_lineage_and_bounds_size() -> None:
    engine = ContextEconomics(max_compacted_chars=100)
    original = item("long", "x" * 500)
    compacted = engine.compact(original)
    assert len(compacted.content) <= 100
    assert compacted.item_id == original.item_id
    assert "compacted" in compacted.tags


def test_cost_budget_and_override_are_enforced() -> None:
    engine = ContextEconomics((ContextBudget(ContextScope.TASK, 80, limit_cost=0.01),))
    result = engine.select(
        (item("a", "a" * 40), item("b", "b" * 40)),
        MODEL,
        active_scopes=(ContextScope.TASK,),
    )
    assert result.estimated_cost <= 0.01
    with pytest.raises(ValueError):
        engine.select((), MODEL, cost_limit_override=-1)


def test_custom_summarizer_is_used_when_compaction_is_needed() -> None:
    engine = ContextEconomics(
        (ContextBudget(ContextScope.TASK, 10),),
        max_compacted_chars=64,
    )
    source = item("long", "original " * 100)
    result = engine.select(
        (source,),
        MODEL,
        active_scopes=(ContextScope.TASK,),
        summarizer=lambda _: "short summary",
    )
    assert result.selected[0].content == "short summary"
    assert "summarized" in result.selected[0].tags


def test_snapshot_store_is_atomic_and_schema_checked(tmp_path: Path) -> None:
    engine = ContextEconomics()
    selection = engine.select((item("a", "hello"),), MODEL)
    store = ContextSnapshotStore(tmp_path / "context.json")
    store.save(selection)
    loaded = store.load()
    assert loaded is not None
    assert loaded["decision_id"] == selection.decision_id
    (tmp_path / "context.json").write_text('{"schema_version": 999}', encoding="utf-8")
    with pytest.raises(ValueError):
        store.load()
