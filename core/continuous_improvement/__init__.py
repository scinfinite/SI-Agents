"""Continuous improvement authority for SI Core."""
from .models import (
    ApprovalRecord,
    CanaryPolicy,
    ChangeRisk,
    ExperimentSpec,
    FailureCluster,
    ImprovementReport,
    ImprovementTarget,
    ImprovementKind,
    OptimizationRecommendation,
    RecommendationStatus,
    RegressionSignal,
    RollbackPlan,
)
from .service import ContinuousImprovement, ImprovementError, ImprovementStore

__all__ = [
    "ApprovalRecord", "CanaryPolicy", "ChangeRisk", "ContinuousImprovement",
    "ExperimentSpec", "FailureCluster", "ImprovementError", "ImprovementReport",
    "ImprovementKind", "ImprovementStore", "ImprovementTarget",
    "OptimizationRecommendation", "RecommendationStatus", "RegressionSignal",
    "RollbackPlan",
]
