from __future__ import annotations

import pytest

from core.continuous_improvement import (
    ApprovalRecord,
    CanaryPolicy,
    ChangeRisk,
    ContinuousImprovement,
    ExperimentSpec,
    ImprovementError,
    ImprovementKind,
    ImprovementStore,
    ImprovementTarget,
    OptimizationRecommendation,
    RecommendationStatus,
)
from core.evaluation import EvaluationSample, EvaluationFailure, GoldenCase, MetricKind, MetricSpec, BenchmarkEngine


def _run():
    case1 = GoldenCase("c1", "x", "ok", (MetricSpec("m", MetricKind.EXACT),))
    case2 = GoldenCase("c2", "y", "ok", (MetricSpec("m", MetricKind.EXACT),))
    return BenchmarkEngine().run(
        suite_id="suite", version="v1", cases=[case1, case2],
        evaluator=lambda value: EvaluationSample(
            "c1" if value == "x" else "c2", "bad", failure=EvaluationFailure.TIMEOUT, reliable=False
        ),
    )


def test_failure_clustering_and_regression_recommendation() -> None:
    engine = ContinuousImprovement()
    run = _run()
    clusters = engine.cluster_failures(run)
    assert clusters[0].failure == "timeout"
    assert clusters[0].count == 2
    signals = engine.detect_regressions({"latency": 0.5}, {"latency": 0.9}, {"latency": 0.1})
    assert signals[0].detected
    recommendations = engine.recommend(run, clusters, signals)
    assert any(item.kind is ImprovementKind.FAILURE_REMEDIATION for item in recommendations)
    assert any(item.target is ImprovementTarget.MODEL for item in recommendations)


def test_analysis_is_durable_and_tamper_evident() -> None:
    store = ImprovementStore()
    report = ContinuousImprovement(store).analyze(
        _run(), baseline={"quality": 1.0}, thresholds={"quality": 0.01}
    )
    assert report.evidence_digest
    assert store.verify()
    store.db.execute("UPDATE improvement_history SET payload_json=? WHERE sequence=1", ('{"tampered":true}',))
    assert not store.verify()


def test_experiment_assignment_and_bounds() -> None:
    spec = ExperimentSpec("exp", "rec", ("control", "candidate"), (1, 3))
    assert ContinuousImprovement.assign_variant(spec, subject="subject") == ContinuousImprovement.assign_variant(spec, subject="subject")
    with pytest.raises(ImprovementError):
        ContinuousImprovement.assign_variant(spec, subject="")


def test_canary_gate_is_fail_closed() -> None:
    policy = CanaryPolicy(minimum_samples=20, maximum_error_rate=0.05, maximum_cost_ratio=1.1, maximum_latency_ratio=1.2, minimum_quality=0.8)
    assert not ContinuousImprovement.canary_allowed(policy, samples=10, error_rate=0.01, cost_ratio=1, latency_ratio=1, quality=0.9)[0]
    ok, reasons = ContinuousImprovement.canary_allowed(policy, samples=20, error_rate=0.01, cost_ratio=1, latency_ratio=1, quality=0.9)
    assert ok and not reasons
    assert not ContinuousImprovement.canary_allowed(policy, samples=20, error_rate=0.2, cost_ratio=1, latency_ratio=1, quality=0.9)[0]


def test_consequential_changes_require_matching_approval() -> None:
    recommendation = OptimizationRecommendation.new(
        kind=ImprovementKind.PERFORMANCE_OPTIMIZATION,
        target=ImprovementTarget.MODEL,
        rationale="measure and improve latency",
        expected_benefit={"latency": 0.1},
        confidence=0.8,
        risk=ChangeRisk.HIGH,
    )
    assert ContinuousImprovement.require_approval(recommendation, None)
    approval = ApprovalRecord("a1", recommendation.recommendation_id, "operator", True, "approved after review")
    assert not ContinuousImprovement.require_approval(recommendation, approval)
    mismatched = ApprovalRecord("a2", "other", "operator", True, "approved")
    assert ContinuousImprovement.require_approval(recommendation, mismatched)


def test_approval_is_secret_safe_and_rollback_requires_active_state() -> None:
    store = ImprovementStore()
    recommendation = OptimizationRecommendation.new(
        kind=ImprovementKind.QUALITY_OPTIMIZATION,
        target=ImprovementTarget.AGENT,
        rationale="measured quality experiment",
        expected_benefit={"quality": 0.1}, confidence=0.7, risk=ChangeRisk.LOW,
    )
    with pytest.raises(ImprovementError):
        store.record_approval(ApprovalRecord("a", recommendation.recommendation_id, "operator", True, "token=secret"))
    with pytest.raises(ImprovementError):
        ContinuousImprovement.rollback_plan(recommendation, "v0", "quality regression")
    active = OptimizationRecommendation(
        recommendation.recommendation_id, recommendation.kind, recommendation.target,
        recommendation.rationale, recommendation.expected_benefit, recommendation.confidence,
        recommendation.risk, recommendation.prerequisites, RecommendationStatus.CANARY,
    )
    plan = ContinuousImprovement.rollback_plan(active, "v0", "quality regression")
    assert plan.previous_version == "v0"
