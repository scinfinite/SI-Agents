from dataclasses import replace

import pytest

from core.capabilities import Capability, CapabilityRegistry, CapabilityStatus
from core.orchestrator.brain import EngineeringBrain
from core.orchestrator.brain_models import Problem, TaskKind
from core.orchestrator.hypothesis import Hypothesis, HypothesisEngine, HypothesisStatus
from core.orchestrator.plan_engine import PlanValidationError, topological_order, validate_plan
from core.orchestrator.plan_models import Plan, PlanStep, StepKind
from core.orchestrator.reasoning import ReasoningEngine, ReasoningStep, ReasoningType
from core.orchestrator.root_cause import CauseNode, RootCauseConfidence, RootCauseEngine
from core.orchestrator.risk import ImpactLevel, RiskEngine
from core.orchestrator.tradeoffs import TradeoffEngine, TradeoffOption
from core.orchestrator.uncertainty import UncertaintyEngine, UncertaintyLevel


def test_brain_decomposes_and_builds_full_verified_plan() -> None:
    problem = Problem(
        "Fix parser failure",
        kind=TaskKind.DEBUGGING,
        acceptance_criteria=("parser accepts valid input", "invalid input returns a clear error"),
    )
    result = EngineeringBrain().build(problem)
    assert len(result.decomposition.subtasks) == 2
    assert [step.kind for step in result.plan.steps] == [
        StepKind.INSPECT, StepKind.RESEARCH, StepKind.EXECUTE, StepKind.TEST,
        StepKind.INSPECT, StepKind.RESEARCH, StepKind.EXECUTE, StepKind.TEST,
        StepKind.VERIFY, StepKind.DOCUMENT,
    ]
    assert result.plan.success_criteria == problem.acceptance_criteria


def test_plan_validation_rejects_cycles() -> None:
    first = PlanStep("first", StepKind.INSPECT)
    second = PlanStep("second", StepKind.TEST, dependencies=(first.id,))
    first = replace(first, dependencies=(second.id,))
    cyclic = Plan("cycle", (first, second), ("done",))
    with pytest.raises(PlanValidationError):
        validate_plan(cyclic)


def test_plan_validation_rejects_unknown_dependencies() -> None:
    step = PlanStep("step", StepKind.TEST, dependencies=("missing",))
    plan = Plan("bad dependency", (step,), ("done",))
    with pytest.raises(PlanValidationError):
        validate_plan(plan)


def test_plan_topological_order_is_dependency_safe() -> None:
    first = PlanStep("first", StepKind.INSPECT)
    second = PlanStep("second", StepKind.TEST, dependencies=(first.id,))
    third = PlanStep("third", StepKind.VERIFY, dependencies=(second.id,))
    assert topological_order((third, second, first)) == (first, second, third)


def test_hypothesis_engine_updates_confidence_with_evidence() -> None:
    hypothesis = Hypothesis("cache is stale", "failure follows cache refresh", confidence=0.5)
    updated = HypothesisEngine().update(hypothesis, supported=True, evidence_id="e1", strength=0.4)
    assert updated.status is HypothesisStatus.SUPPORTED
    assert updated.confidence == pytest.approx(0.7)
    assert updated.evidence == ("e1",)


def test_hypothesis_engine_reduces_confidence_when_refuted() -> None:
    hypothesis = Hypothesis("cache is stale", "failure follows cache refresh", confidence=0.8)
    updated = HypothesisEngine().update(hypothesis, supported=False, evidence_id="e2", strength=0.5)
    assert updated.status is HypothesisStatus.REFUTED
    assert updated.confidence == pytest.approx(0.4)


def test_reasoning_engine_chains_confidence() -> None:
    steps = (
        ReasoningStep("a", "because", "b", ReasoningType.DEDUCTIVE, confidence=0.8),
        ReasoningStep("b", "because", "c", ReasoningType.CAUSAL, confidence=0.5),
    )
    assert ReasoningEngine().chain(steps) == pytest.approx(0.4)


def test_root_cause_engine_classifies_evidence_strength() -> None:
    nodes = (CauseNode("bad input"), CauseNode("parser branch"))
    result = RootCauseEngine().analyze(
        problem="parser fails", root_cause="bad input", causes=nodes, evidence=("e1", "e2")
    )
    assert result.confidence is RootCauseConfidence.HIGH


def test_root_cause_engine_rejects_unknown_parent() -> None:
    node = CauseNode("bad branch", parents=("missing",))
    with pytest.raises(ValueError):
        RootCauseEngine().analyze(
            problem="failure", root_cause="bad branch", causes=(node,), evidence=("e1",)
        )


def test_tradeoff_engine_selects_highest_scored_option() -> None:
    options = (TradeoffOption("A", score=0.4), TradeoffOption("B", score=0.8))
    result = TradeoffEngine().analyze("storage", options, rationale="higher score")
    assert result.selected == "B"


def test_uncertainty_engine_marks_missing_evidence() -> None:
    result = UncertaintyEngine().assess(
        "runtime behavior", evidence_count=0, missing_evidence=("production trace",)
    )
    assert result.level is UncertaintyLevel.MEDIUM


def test_risk_engine_maps_likelihood_to_impact() -> None:
    result = RiskEngine().assess("data loss", likelihood=0.9, rationale="destructive path")
    assert result.level is ImpactLevel.CRITICAL


def test_brain_can_select_validated_capability() -> None:
    registry = CapabilityRegistry()
    registry.register(Capability(
        name="debug-python", category="debugging", status=CapabilityStatus.VALIDATED,
        verification=("test suite passes",), confidence=0.9, health=0.9, benchmark_score=0.8,
    ))
    problem = Problem("debug", kind=TaskKind.DEBUGGING, acceptance_criteria=("fixed",))
    result = EngineeringBrain(registry).build(problem, category="debugging")
    assert result.selected_capabilities[0].name == "debug-python"
