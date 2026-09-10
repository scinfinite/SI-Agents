from pathlib import Path

import pytest

from core.capabilities.models import Capability, CapabilityStatus
from core.capabilities.registry import CapabilityRegistry
from core.learning.engine import ImprovementEngine
from core.learning.evaluator import ImprovementEvaluator
from core.learning.intelligence import CapabilityIntelligence
from core.learning.models import (
    EvaluationResult,
    EvidenceItem,
    ImprovementProposal,
    ImprovementStatus,
)
from core.learning.registry import ImprovementRegistry
from core.learning.store import ImprovementStore


def evidence(*names: str, verified: bool = True) -> tuple[EvidenceItem, ...]:
    return tuple(
        EvidenceItem(name, f"verified observation from {name}", verified)
        for name in names
    )


def proposal(**kwargs: object) -> ImprovementProposal:
    defaults = {
        "target": "router",
        "summary": "improve ranking",
        "rationale": "measured latency issue",
        "change_ref": "change-1",
        "evidence": evidence("test", "benchmark"),
    }
    defaults.update(kwargs)
    return ImprovementProposal(**defaults)


def evaluator(
    score: float = 0.9, *, safety: bool = True, regression: bool = True
) -> ImprovementEvaluator:
    return ImprovementEvaluator(
        benchmark=lambda _: (score, True, evidence("benchmark")),
        regression=lambda _: (
            regression,
            () if regression else ("regression",),
            evidence("regression"),
        ),
        safety=lambda _: (safety, evidence("safety")),
    )


def test_evidence_count_and_model_validation() -> None:
    assert proposal().verified_evidence_count == 2
    with pytest.raises(ValueError):
        ImprovementProposal("x", "y", "z", "r", ())


def test_evaluation_fails_closed_when_gates_missing() -> None:
    evaluator_without_benchmark = ImprovementEvaluator(
        regression=lambda _: (True, (), ()),
        safety=lambda _: (True, ()),
    )
    with pytest.raises(ValueError, match="Benchmark"):
        evaluator_without_benchmark.evaluate(proposal(), score_before=0.5)


def test_engine_requires_all_gates_before_approval() -> None:
    registry = ImprovementRegistry()
    engine = ImprovementEngine(registry, evaluator(score=0.4))
    item = engine.propose(proposal())
    engine.evaluate(item.id, score_before=0.5)
    with pytest.raises(ValueError, match="passing"):
        engine.approve(item.id)


def test_engine_full_lifecycle_and_rollback() -> None:
    registry = ImprovementRegistry()
    engine = ImprovementEngine(registry, evaluator(score=0.8))
    item = engine.propose(proposal())
    engine.evaluate(item.id, score_before=0.8)
    engine.approve(item.id)
    applied = engine.apply(item.id, lambda _: None)
    assert applied.status is ImprovementStatus.APPLIED
    rolled = engine.rollback(item.id, lambda _: None)
    assert rolled.status is ImprovementStatus.ROLLED_BACK


def test_apply_requires_approval() -> None:
    registry = ImprovementRegistry()
    engine = ImprovementEngine(registry, evaluator())
    item = engine.propose(proposal())
    with pytest.raises(ValueError, match="approved"):
        engine.apply(item.id, lambda _: None)


def test_registry_rejects_invalid_transition() -> None:
    registry = ImprovementRegistry()
    item = registry.register(proposal())
    with pytest.raises(ValueError, match="Invalid improvement"):
        registry.transition(item.id, ImprovementStatus.APPLIED)


def test_failed_safety_blocks_approval() -> None:
    registry = ImprovementRegistry()
    engine = ImprovementEngine(registry, evaluator(safety=False))
    item = engine.propose(proposal())
    engine.evaluate(item.id, score_before=0.5)
    with pytest.raises(ValueError):
        engine.approve(item.id)


def test_failed_regression_blocks_approval() -> None:
    registry = ImprovementRegistry()
    engine = ImprovementEngine(registry, evaluator(regression=False))
    item = engine.propose(proposal())
    engine.evaluate(item.id, score_before=0.5)
    with pytest.raises(ValueError):
        engine.approve(item.id)


def test_proposal_requires_verified_evidence() -> None:
    registry = ImprovementRegistry()
    engine = ImprovementEngine(registry, evaluator())
    unverified = proposal(evidence=evidence("one", "two", verified=False))
    with pytest.raises(ValueError, match="verified evidence"):
        engine.propose(unverified)


def test_capability_intelligence_is_deterministic() -> None:
    registry = CapabilityRegistry()
    capability = registry.register(
        Capability(
            "code",
            "engineering",
            CapabilityStatus.VALIDATED,
            verification=("tests",),
            evidence=("e1", "e2"),
            confidence=0.9,
            health=1.0,
            benchmark_score=0.9,
        )
    )
    intelligence = CapabilityIntelligence(registry)
    first = intelligence.score(capability)
    second = intelligence.score(capability)
    assert first == second
    assert first.readiness > 0.8


def test_blocked_capability_has_zero_readiness() -> None:
    registry = CapabilityRegistry()
    capability = registry.register(Capability("unsafe", "security", CapabilityStatus.BLOCKED))
    assert CapabilityIntelligence(registry).score(capability).readiness == 0.0


def test_unknown_health_is_not_executable() -> None:
    registry = CapabilityRegistry()
    registry.register(
        Capability(
            "unknown-health",
            "engineering",
            CapabilityStatus.VALIDATED,
            verification=("tests",),
            evidence=("e1", "e2"),
            benchmark_score=0.9,
        )
    )
    assert CapabilityIntelligence(registry).executable_candidates() == ()


def test_intelligence_does_not_treat_experimental_as_executable() -> None:
    registry = CapabilityRegistry()
    registry.register(
        Capability("x", "engineering", CapabilityStatus.EXPERIMENTAL, health=1.0)
    )
    assert CapabilityIntelligence(registry).executable_candidates() == ()


def test_capability_ranking_is_stable() -> None:
    registry = CapabilityRegistry()
    for name in ("b", "a"):
        registry.register(
            Capability(
                name,
                "engineering",
                CapabilityStatus.VALIDATED,
                verification=("v",),
                evidence=("e",),
                health=1.0,
                benchmark_score=0.8,
            )
        )
    ranked = CapabilityIntelligence(registry).rank()
    assert [item.capability_id for item in ranked] == [
        registry.get_by_name("a").id,
        registry.get_by_name("b").id,
    ]


def test_store_round_trip(tmp_path: Path) -> None:
    item = proposal()
    path = tmp_path / "learning.json"
    store = ImprovementStore()
    store.save(path, (item,))
    loaded = store.load(path)
    assert loaded == (item,)


def test_store_rejects_non_list(tmp_path: Path) -> None:
    path = tmp_path / "learning.json"
    path.write_text("{}", encoding="utf-8")
    with pytest.raises(TypeError, match="list"):
        ImprovementStore().load(path)


def test_evaluation_rejects_score_drop_marked_passing() -> None:
    with pytest.raises(ValueError, match="lower score"):
        EvaluationResult(True, True, True, 0.9, 0.8)


def test_engine_does_not_mutate_on_apply_failure() -> None:
    registry = ImprovementRegistry()
    engine = ImprovementEngine(registry, evaluator())
    item = engine.propose(proposal())
    engine.evaluate(item.id, score_before=0.8)
    engine.approve(item.id)
    with pytest.raises(RuntimeError):
        engine.apply(
            item.id,
            lambda _: (_ for _ in ()).throw(RuntimeError("boom")),
        )
    assert registry.get(item.id).status is ImprovementStatus.APPROVED


def test_rollback_failure_preserves_applied_state() -> None:
    registry = ImprovementRegistry()
    engine = ImprovementEngine(registry, evaluator())
    item = engine.propose(proposal())
    engine.evaluate(item.id, score_before=0.8)
    engine.approve(item.id)
    engine.apply(item.id, lambda _: None)
    with pytest.raises(RuntimeError):
        engine.rollback(
            item.id,
            lambda _: (_ for _ in ()).throw(RuntimeError("boom")),
        )
    assert registry.get(item.id).status is ImprovementStatus.APPLIED
