"""Phase 60 evaluation and benchmarking authority."""
from .models import (
    CaseResult,
    EvaluationDimension,
    EvaluationFailure,
    EvaluationReport,
    EvaluationRun,
    EvaluationSample,
    ExperimentAssignment,
    ExperimentSpec,
    GoldenCase,
    HumanReview,
    MetricKind,
    MetricScore,
    MetricSpec,
    Regression,
    ReleaseGatePolicy,
)
from .scoring import score_case, score_metric
from .service import BenchmarkEngine, EvaluationError, EvaluationStore
__all__=[
    "BenchmarkEngine","CaseResult","EvaluationDimension","EvaluationFailure",
    "EvaluationError","EvaluationReport","EvaluationRun","EvaluationSample",
    "EvaluationStore","ExperimentAssignment","ExperimentSpec","GoldenCase",
    "HumanReview","MetricKind","MetricScore","MetricSpec","Regression",
    "ReleaseGatePolicy","score_case","score_metric",
]
