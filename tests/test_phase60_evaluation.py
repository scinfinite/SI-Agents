from __future__ import annotations

import json

import pytest

from core.evaluation import (
    BenchmarkEngine,
    EvaluationDimension,
    EvaluationFailure,
    EvaluationSample,
    ExperimentSpec,
    GoldenCase,
    HumanReview,
    MetricKind,
    MetricSpec,
    ReleaseGatePolicy,
)
from core.evaluation.service import EvaluationError, EvaluationStore


def test_all_metric_modes_and_thresholds() -> None:
    cases = [
        (MetricSpec("exact", MetricKind.EXACT), "ok", "ok"),
        (MetricSpec("normalized", MetricKind.NORMALIZED), "Hello   World", "hello world"),
        (MetricSpec("contains", MetricKind.CONTAINS), "a needle here", "needle"),
        (MetricSpec("json", MetricKind.JSON_EQUAL), '{"a":1}', '{"a": 1}'),
        (MetricSpec("num", MetricKind.NUMERIC_ABS, tolerance=0.5), 10.2, 10),
        (MetricSpec("rubric", MetricKind.RUBRIC), "score: 0.8", "ignored"),
    ]
    for metric, actual, expected in cases:
        case = GoldenCase(metric.metric_id, "x", expected, (metric,))
        from core.evaluation import score_metric

        result = score_metric(case, metric.metric_id, actual)
        assert 0 <= result.score <= 1
    with pytest.raises(ValueError):
        MetricSpec("bad", MetricKind.NUMERIC_ABS)


def test_failures_are_recorded_and_never_count_as_pass() -> None:
    engine = BenchmarkEngine()
    case = GoldenCase("c1", "input", "expected", (MetricSpec("m", MetricKind.EXACT),))
    run = engine.run(
        suite_id="suite",
        version="v1",
        cases=[case],
        evaluator=lambda _: EvaluationSample(
            "c1", "expected", failure=EvaluationFailure.TIMEOUT, reliable=False
        ),
    )
    assert not run.passed
    assert run.results[0].failure is EvaluationFailure.TIMEOUT
    assert run.results[0].weighted_score == 0


def test_secret_rejection_duplicate_guard_and_store_review() -> None:
    engine = BenchmarkEngine()
    metric = MetricSpec("m", MetricKind.EXACT)
    with pytest.raises(EvaluationError):
        engine.run(
            suite_id="suite",
            version="v1",
            cases=[GoldenCase("secret", "api_key=hidden", "x", (metric,))],
            evaluator=lambda _: EvaluationSample("secret", "x"),
        )
    case = GoldenCase("c1", "x", "x", (metric,))
    with pytest.raises(EvaluationError):
        engine.run(
            suite_id="suite",
            version="v1",
            cases=[case, case],
            evaluator=lambda _: EvaluationSample("c1", "x"),
        )
    store = EvaluationStore()
    review = HumanReview.new("run", "case", "reviewer", 0.9, "strong result")
    store.record_review(review)
    assert store.review_average("run", "case") == 0.9
    assert len(store.recent("missing")) == 0
    with pytest.raises(EvaluationError):
        store.record_review(HumanReview.new("run", "case", "reviewer", 0.9, "token=secret"))


def test_regression_release_gate_and_deterministic_ab() -> None:
    engine = BenchmarkEngine()
    case = GoldenCase("c1", "x", "x", (MetricSpec("m", MetricKind.EXACT),))
    run = engine.run(
        suite_id="suite",
        version="v1",
        cases=[case],
        evaluator=lambda _: EvaluationSample("c1", "x", duration_ms=10, cost=0.1),
    )
    report = engine.report(run, baseline={"quality": 1.0}, thresholds={"quality": 0.01})
    assert report.case_count == 1
    assert report.evidence_digest
    ok, reasons = engine.release_gate(report, ReleaseGatePolicy(minimum_score=0.9, max_regressions=0))
    assert ok, reasons
    bad = engine.regressions({"quality": 0.7}, {"quality": 0.9}, {"quality": 0.05})
    assert bad[0].detected
    spec = ExperimentSpec("exp", ("A", "B"), (1, 3))
    assert engine.assign_variant(spec, subject="subject-1") == engine.assign_variant(spec, subject="subject-1")


def test_release_gate_enforces_cost_and_latency_budgets() -> None:
    engine = BenchmarkEngine()
    case = GoldenCase("c1", "x", "x", (MetricSpec("m", MetricKind.EXACT),))
    run = engine.run(
        suite_id="suite",
        version="v1",
        cases=[case],
        evaluator=lambda _: EvaluationSample("c1", "x", duration_ms=250, cost=2.5),
    )
    report = engine.report(run)
    ok, reasons = engine.release_gate(
        report,
        ReleaseGatePolicy(maximum_cost=2.0, maximum_latency_ms=200),
    )
    assert not ok
    assert "maximum cost exceeded" in reasons
    assert "maximum latency exceeded" in reasons


def test_persisted_evidence_detects_tampering_and_actual_secret_is_rejected() -> None:
    store = EvaluationStore()
    engine = BenchmarkEngine(store)
    case = GoldenCase("c1", "x", "x", (MetricSpec("m", MetricKind.EXACT),))
    run = engine.run(
        suite_id="suite",
        version="v1",
        cases=[case],
        evaluator=lambda _: EvaluationSample("c1", "safe"),
    )
    assert store.verify_run(run.run_id)
    store.db.execute(
        "UPDATE evaluation_runs SET payload_json=? WHERE run_id=?",
        (json.dumps({"tampered": True}), run.run_id),
    )
    assert not store.verify_run(run.run_id)
    with pytest.raises(EvaluationError):
        engine.run(
            suite_id="suite",
            version="v1",
            cases=[case],
            evaluator=lambda _: EvaluationSample("c1", "api_key=leaked"),
        )


def test_invalid_experiment_inputs_and_empty_report_fail_closed() -> None:
    with pytest.raises(ValueError):
        ExperimentSpec("exp", ("", "B"))
    with pytest.raises(EvaluationError):
        BenchmarkEngine().report(
            type("Empty", (), {"results": (), "score": 0.0})()
        )


def test_report_summary_is_json_safe() -> None:
    engine = BenchmarkEngine()
    case = GoldenCase(
        "c1",
        {"question": "q"},
        {"answer": 1},
        (MetricSpec("json", MetricKind.JSON_EQUAL),),
    )
    run = engine.run(
        suite_id="suite",
        version="v1",
        cases=[case],
        evaluator=lambda _: EvaluationSample("c1", {"answer": 1}),
    )
    report = engine.report(run)
    json.dumps(report.summary)
    assert report.dimensions[EvaluationDimension.SECURITY.value] == 1.0
