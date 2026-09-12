"""Evaluation, benchmark, experiment, and release-gate contracts."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
import time
import uuid
from typing import Any, Mapping


class MetricKind(StrEnum):
    EXACT = "exact"
    NORMALIZED = "normalized"
    CONTAINS = "contains"
    JSON_EQUAL = "json_equal"
    NUMERIC_ABS = "numeric_abs"
    RUBRIC = "rubric"


class EvaluationDimension(StrEnum):
    QUALITY = "quality"
    RELIABILITY = "reliability"
    SECURITY = "security"
    COST = "cost"
    LATENCY = "latency"


class EvaluationFailure(StrEnum):
    TIMEOUT = "timeout"
    AUTHORIZATION = "authorization"
    TOOL_ERROR = "tool_error"
    MODEL_ERROR = "model_error"
    VALIDATION_ERROR = "validation_error"
    SECURITY_VIOLATION = "security_violation"
    INFRASTRUCTURE = "infrastructure"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class MetricSpec:
    metric_id: str
    kind: MetricKind
    weight: float = 1.0
    threshold: float = 1.0
    tolerance: float | None = None
    target: Any = None

    def __post_init__(self) -> None:
        if not self.metric_id.strip() or self.weight <= 0 or not 0 <= self.threshold <= 1:
            raise ValueError("invalid metric specification")
        if self.kind is MetricKind.NUMERIC_ABS:
            if self.tolerance is None or self.tolerance <= 0:
                raise ValueError("numeric metric requires positive tolerance")


@dataclass(frozen=True, slots=True)
class GoldenCase:
    case_id: str
    input: Any
    expected: Any
    metrics: tuple[MetricSpec, ...]
    tags: tuple[str, ...] = ()
    security_risk: str = "low"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.case_id.strip() or not self.metrics or len(self.metrics) > 32:
            raise ValueError("invalid golden case")
        if len({metric.metric_id for metric in self.metrics}) != len(self.metrics):
            raise ValueError("duplicate metric ids")


@dataclass(frozen=True, slots=True)
class EvaluationSample:
    case_id: str
    actual: Any
    duration_ms: float = 0.0
    cost: float = 0.0
    passed_security: bool = True
    reliable: bool = True
    failure: EvaluationFailure | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.duration_ms < 0 or self.cost < 0:
            raise ValueError("duration/cost must be non-negative")


@dataclass(frozen=True, slots=True)
class MetricScore:
    metric_id: str
    score: float
    passed: bool
    details: str = ""


@dataclass(frozen=True, slots=True)
class CaseResult:
    case_id: str
    scores: tuple[MetricScore, ...]
    weighted_score: float
    passed: bool
    duration_ms: float
    cost: float
    reliable: bool
    security_passed: bool
    failure: EvaluationFailure | None = None


@dataclass(frozen=True, slots=True)
class EvaluationRun:
    run_id: str
    suite_id: str
    version: str
    started_at: float
    completed_at: float
    results: tuple[CaseResult, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def score(self) -> float:
        return (
            sum(result.weighted_score for result in self.results) / len(self.results)
            if self.results
            else 0.0
        )

    @property
    def passed(self) -> bool:
        return bool(self.results) and all(result.passed for result in self.results)


@dataclass(frozen=True, slots=True)
class Regression:
    dimension: EvaluationDimension
    current: float
    baseline: float
    delta: float
    threshold: float
    detected: bool


@dataclass(frozen=True, slots=True)
class EvaluationReport:
    run_id: str
    suite_id: str
    version: str
    score: float
    passed: bool
    case_count: int
    regressions: tuple[Regression, ...]
    dimensions: Mapping[str, float]
    summary: Mapping[str, Any]
    evidence_digest: str


@dataclass(frozen=True, slots=True)
class ExperimentAssignment:
    experiment_id: str
    subject: str
    variant: str
    bucket: int


@dataclass(frozen=True, slots=True)
class ExperimentSpec:
    experiment_id: str
    variants: tuple[str, ...]
    weights: tuple[int, ...] | None = None

    def __post_init__(self) -> None:
        if (
            not self.experiment_id.strip()
            or not self.variants
            or len(self.variants) > 16
            or len(set(self.variants)) != len(self.variants)
            or any(not variant.strip() for variant in self.variants)
        ):
            raise ValueError("invalid variants")
        if self.weights is not None and (
            len(self.weights) != len(self.variants)
            or any(weight <= 0 for weight in self.weights)
            or sum(self.weights) > 1_000_000
        ):
            raise ValueError("invalid experiment weights")


@dataclass(frozen=True, slots=True)
class ReleaseGatePolicy:
    minimum_score: float = 0.8
    minimum_dimensions: Mapping[str, float] = field(default_factory=dict)
    max_regressions: int = 0
    maximum_cost: float | None = None
    maximum_latency_ms: float | None = None

    def __post_init__(self) -> None:
        if not 0 <= self.minimum_score <= 1 or self.max_regressions < 0:
            raise ValueError("invalid gate policy")
        if any(not 0 <= float(value) <= 1 for value in self.minimum_dimensions.values()):
            raise ValueError("dimension thresholds must be between zero and one")
        if self.maximum_cost is not None and self.maximum_cost < 0:
            raise ValueError("maximum cost must be non-negative")
        if self.maximum_latency_ms is not None and self.maximum_latency_ms < 0:
            raise ValueError("maximum latency must be non-negative")


@dataclass(frozen=True, slots=True)
class HumanReview:
    review_id: str
    run_id: str
    case_id: str
    reviewer_id: str
    score: float
    rationale: str
    created_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        if not all(
            value.strip()
            for value in (
                self.review_id,
                self.run_id,
                self.case_id,
                self.reviewer_id,
                self.rationale,
            )
        ) or not 0 <= self.score <= 1:
            raise ValueError("invalid human review")

    @classmethod
    def new(
        cls,
        run_id: str,
        case_id: str,
        reviewer_id: str,
        score: float,
        rationale: str,
    ) -> "HumanReview":
        return cls(
            f"review_{uuid.uuid4().hex}",
            run_id,
            case_id,
            reviewer_id,
            score,
            rationale,
        )
