"""Continuous-improvement contracts and immutable governance records."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
import time
import uuid
from typing import Any, Mapping


class ImprovementKind(StrEnum):
    FAILURE_REMEDIATION = "failure_remediation"
    REGRESSION_REDUCTION = "regression_reduction"
    COST_OPTIMIZATION = "cost_optimization"
    RELIABILITY_OPTIMIZATION = "reliability_optimization"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    QUALITY_OPTIMIZATION = "quality_optimization"


class ImprovementTarget(StrEnum):
    AGENT = "agent"
    TEAM = "team"
    MODEL = "model"
    ROUTING = "routing"
    WORKFLOW = "workflow"


class ChangeRisk(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecommendationStatus(StrEnum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANARY = "canary"
    PROMOTED = "promoted"
    ROLLED_BACK = "rolled_back"


@dataclass(frozen=True, slots=True)
class FailureCluster:
    cluster_id: str
    failure: str
    case_ids: tuple[str, ...]
    count: int
    rate: float
    signature: str

    def __post_init__(self) -> None:
        if not self.cluster_id.strip() or not self.failure.strip() or not self.case_ids:
            raise ValueError("invalid failure cluster")
        if self.count != len(self.case_ids) or self.count <= 0 or not 0 <= self.rate <= 1:
            raise ValueError("invalid failure cluster counts")
        if not self.signature.strip():
            raise ValueError("failure signature is required")


@dataclass(frozen=True, slots=True)
class RegressionSignal:
    dimension: str
    current: float
    baseline: float
    delta: float
    threshold: float
    detected: bool


@dataclass(frozen=True, slots=True)
class OptimizationRecommendation:
    recommendation_id: str
    kind: ImprovementKind
    target: ImprovementTarget
    rationale: str
    expected_benefit: Mapping[str, float]
    confidence: float
    risk: ChangeRisk
    prerequisites: tuple[str, ...] = ()
    status: RecommendationStatus = RecommendationStatus.PROPOSED
    created_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        if not self.recommendation_id.strip() or not self.rationale.strip():
            raise ValueError("invalid recommendation")
        if not 0 <= self.confidence <= 1 or not self.expected_benefit:
            raise ValueError("invalid recommendation confidence/benefit")
        if any(not key.strip() or not isinstance(value, (int, float)) for key, value in self.expected_benefit.items()):
            raise ValueError("invalid expected benefit")
        if any(not item.strip() for item in self.prerequisites):
            raise ValueError("invalid recommendation prerequisite")

    @classmethod
    def new(
        cls,
        *,
        kind: ImprovementKind,
        target: ImprovementTarget,
        rationale: str,
        expected_benefit: Mapping[str, float],
        confidence: float,
        risk: ChangeRisk,
        prerequisites: tuple[str, ...] = (),
    ) -> "OptimizationRecommendation":
        return cls(
            f"improve_{uuid.uuid4().hex}",
            kind,
            target,
            rationale,
            dict(expected_benefit),
            confidence,
            risk,
            prerequisites,
        )


@dataclass(frozen=True, slots=True)
class ExperimentSpec:
    experiment_id: str
    recommendation_id: str
    variants: tuple[str, ...]
    weights: tuple[int, ...] | None = None
    sample_size: int = 100
    approval_required: bool = True

    def __post_init__(self) -> None:
        if not self.experiment_id.strip() or not self.recommendation_id.strip():
            raise ValueError("experiment identity is required")
        if not 2 <= len(self.variants) <= 8 or len(set(self.variants)) != len(self.variants):
            raise ValueError("experiments require 2-8 unique variants")
        if any(not variant.strip() or len(variant) > 128 for variant in self.variants):
            raise ValueError("invalid experiment variant")
        if self.weights is not None and (
            len(self.weights) != len(self.variants)
            or any(weight <= 0 for weight in self.weights)
            or sum(self.weights) > 1_000_000
        ):
            raise ValueError("invalid experiment weights")
        if not 2 <= self.sample_size <= 1_000_000:
            raise ValueError("invalid experiment sample size")


@dataclass(frozen=True, slots=True)
class CanaryPolicy:
    minimum_samples: int = 20
    maximum_error_rate: float = 0.05
    maximum_cost_ratio: float = 1.10
    maximum_latency_ratio: float = 1.20
    minimum_quality: float = 0.80
    require_human_approval: bool = True

    def __post_init__(self) -> None:
        if self.minimum_samples <= 0 or not 0 <= self.maximum_error_rate <= 1:
            raise ValueError("invalid canary policy")
        if self.maximum_cost_ratio < 0 or self.maximum_latency_ratio < 0:
            raise ValueError("invalid canary ratios")
        if not 0 <= self.minimum_quality <= 1:
            raise ValueError("invalid canary quality")


@dataclass(frozen=True, slots=True)
class RollbackPlan:
    rollback_id: str
    recommendation_id: str
    previous_version: str
    trigger: str
    authorized: bool = False

    def __post_init__(self) -> None:
        if not all(value.strip() for value in (self.rollback_id, self.recommendation_id, self.previous_version, self.trigger)):
            raise ValueError("invalid rollback plan")


@dataclass(frozen=True, slots=True)
class ApprovalRecord:
    approval_id: str
    recommendation_id: str
    approver_id: str
    approved: bool
    rationale: str
    created_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        if not all(value.strip() for value in (self.approval_id, self.recommendation_id, self.approver_id, self.rationale)):
            raise ValueError("invalid approval")


@dataclass(frozen=True, slots=True)
class ImprovementReport:
    report_id: str
    source_run_id: str
    clusters: tuple[FailureCluster, ...]
    regressions: tuple[RegressionSignal, ...]
    recommendations: tuple[OptimizationRecommendation, ...]
    evidence_digest: str

    def __post_init__(self) -> None:
        if not self.report_id.strip() or not self.source_run_id.strip() or not self.evidence_digest.strip():
            raise ValueError("invalid improvement report")
