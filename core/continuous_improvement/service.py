"""Continuous-improvement analysis, recommendation, experimentation, and rollout authority."""
from __future__ import annotations

import hashlib
import json
import sqlite3
from collections import defaultdict
from collections.abc import Mapping, Sequence
import time
import uuid

from core.evaluation.models import EvaluationRun
from core.security.platform import SecretScanner

from .models import (
    ApprovalRecord, CanaryPolicy, ChangeRisk, ExperimentSpec, FailureCluster,
    ImprovementReport, ImprovementTarget, ImprovementKind, OptimizationRecommendation,
    RecommendationStatus, RegressionSignal, RollbackPlan,
)

MAX_CLUSTERS = 256
MAX_CASES = 10_000


class ImprovementError(ValueError):
    """Continuous-improvement contract violation."""


def _safe(value: object, context: str) -> None:
    try:
        encoded = json.dumps(value, default=str, ensure_ascii=False)
    except (TypeError, ValueError) as exc:
        raise ImprovementError(f"{context} is not serializable") from exc
    if len(encoded.encode("utf-8")) > 256 * 1024:
        raise ImprovementError(f"{context} exceeds payload limit")
    if SecretScanner.contains_secret(encoded):
        raise ImprovementError(f"secret-like data in {context}")


def _approval_dict(approval: ApprovalRecord) -> dict[str, object]:
    return {
        "approval_id": approval.approval_id,
        "recommendation_id": approval.recommendation_id,
        "approver_id": approval.approver_id,
        "approved": approval.approved,
    }


def _cluster_dict(cluster: FailureCluster) -> dict[str, object]:
    return {
        "id": cluster.cluster_id,
        "failure": cluster.failure,
        "count": cluster.count,
        "rate": cluster.rate,
        "signature": cluster.signature,
    }


def _regression_dict(signal: RegressionSignal) -> dict[str, object]:
    return {
        "dimension": signal.dimension,
        "current": signal.current,
        "baseline": signal.baseline,
        "delta": signal.delta,
        "threshold": signal.threshold,
        "detected": signal.detected,
    }


class ImprovementStore:
    """Durable, tamper-evident history for improvement decisions."""

    def __init__(self, path: str = ":memory:") -> None:
        self.db = sqlite3.connect(path, isolation_level=None, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript(
            """CREATE TABLE IF NOT EXISTS improvement_history(
            sequence INTEGER PRIMARY KEY AUTOINCREMENT, record_id TEXT UNIQUE NOT NULL,
            kind TEXT NOT NULL, payload_json TEXT NOT NULL, previous_digest TEXT NOT NULL,
            digest TEXT NOT NULL, created_at REAL NOT NULL);
            CREATE TABLE IF NOT EXISTS improvement_approvals(
            approval_id TEXT PRIMARY KEY, recommendation_id TEXT NOT NULL, approver_id TEXT NOT NULL,
            approved INTEGER NOT NULL, rationale TEXT NOT NULL, created_at REAL NOT NULL);"""
        )

    def close(self) -> None:
        self.db.close()

    def append(self, kind: str, record: object) -> str:
        _safe(record, f"{kind} record")
        payload = json.dumps(
            record, default=str, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        previous = self.db.execute(
            "SELECT digest FROM improvement_history ORDER BY sequence DESC LIMIT 1"
        ).fetchone()
        previous_digest = previous["digest"] if previous else "0" * 64
        digest = hashlib.sha256(f"{previous_digest}|{kind}|{payload}".encode()).hexdigest()
        record_id = f"impr_{uuid.uuid4().hex}"
        self.db.execute(
            "INSERT INTO improvement_history(record_id,kind,payload_json,previous_digest,digest,created_at) VALUES(?,?,?,?,?,?)",
            (record_id, kind, payload, previous_digest, digest, time.time()),
        )
        return digest

    def verify(self) -> bool:
        previous = "0" * 64
        rows = self.db.execute(
            "SELECT kind,payload_json,previous_digest,digest FROM improvement_history ORDER BY sequence"
        ).fetchall()
        for row in rows:
            if row["previous_digest"] != previous:
                return False
            expected = hashlib.sha256(
                f"{previous}|{row['kind']}|{row['payload_json']}".encode()
            ).hexdigest()
            if expected != row["digest"]:
                return False
            previous = expected
        return True

    def record_approval(self, approval: ApprovalRecord) -> None:
        _safe(approval.rationale, "approval rationale")
        self.db.execute(
            "INSERT INTO improvement_approvals VALUES(?,?,?,?,?,?)",
            (approval.approval_id, approval.recommendation_id, approval.approver_id,
             int(approval.approved), approval.rationale, approval.created_at),
        )
        self.append("approval", _approval_dict(approval))


class ContinuousImprovement:
    """Derives bounded, explainable improvement proposals without mutating runtime authority."""

    def __init__(self, store: ImprovementStore | None = None) -> None:
        self.store = store or ImprovementStore()

    @staticmethod
    def cluster_failures(run: EvaluationRun) -> tuple[FailureCluster, ...]:
        if len(run.results) > MAX_CASES:
            raise ImprovementError("evaluation run exceeds case limit")
        groups: dict[str, list[str]] = defaultdict(list)
        for result in run.results:
            if result.failure is not None:
                groups[result.failure.value].append(result.case_id)
            elif not result.passed:
                groups["quality_failure"].append(result.case_id)
        total = max(1, len(run.results))
        clusters = []
        for failure, case_ids in sorted(groups.items()):
            signature = hashlib.sha256(failure.encode()).hexdigest()
            clusters.append(
                FailureCluster(
                    f"cluster_{signature[:16]}", failure, tuple(case_ids),
                    len(case_ids), len(case_ids) / total, signature,
                )
            )
        if len(clusters) > MAX_CLUSTERS:
            raise ImprovementError("too many failure clusters")
        return tuple(clusters)

    @staticmethod
    def detect_regressions(
        current: Mapping[str, float],
        baseline: Mapping[str, float],
        thresholds: Mapping[str, float],
    ) -> tuple[RegressionSignal, ...]:
        signals = []
        for name, baseline_value in baseline.items():
            now, base = float(current.get(name, 0.0)), float(baseline_value)
            threshold = max(0.0, float(thresholds.get(name, 0.0)))
            delta = now - base
            signals.append(
                RegressionSignal(name, now, base, delta, threshold, delta < -threshold)
            )
        return tuple(signals)

    @staticmethod
    def recommend(
        run: EvaluationRun,
        clusters: Sequence[FailureCluster],
        regressions: Sequence[RegressionSignal] = (),
    ) -> tuple[OptimizationRecommendation, ...]:
        recommendations: list[OptimizationRecommendation] = []
        if clusters:
            top = max(clusters, key=lambda item: (item.rate, item.failure))
            recommendations.append(
                OptimizationRecommendation.new(
                    kind=ImprovementKind.FAILURE_REMEDIATION,
                    target=ImprovementTarget.WORKFLOW,
                    rationale=f"Address dominant failure cluster {top.failure} affecting {top.count} cases.",
                    expected_benefit={"reliability": min(1.0, top.rate)},
                    confidence=min(0.99, 0.60 + top.rate / 2),
                    risk=ChangeRisk.MEDIUM,
                    prerequisites=(f"inspect:{top.cluster_id}",),
                )
            )
        for signal in regressions:
            if not signal.detected:
                continue
            if signal.dimension == "cost":
                kind, target = ImprovementKind.COST_OPTIMIZATION, ImprovementTarget.ROUTING
            elif signal.dimension == "latency":
                kind, target = ImprovementKind.PERFORMANCE_OPTIMIZATION, ImprovementTarget.MODEL
            elif signal.dimension == "reliability":
                kind, target = ImprovementKind.RELIABILITY_OPTIMIZATION, ImprovementTarget.ROUTING
            else:
                kind, target = ImprovementKind.QUALITY_OPTIMIZATION, ImprovementTarget.AGENT
            recommendations.append(
                OptimizationRecommendation.new(
                    kind=kind,
                    target=target,
                    rationale=f"Reverse {signal.dimension} regression of {signal.delta:.4f} against baseline.",
                    expected_benefit={signal.dimension: min(1.0, abs(signal.delta))},
                    confidence=0.75,
                    risk=(
                        ChangeRisk.HIGH
                        if signal.dimension in {"security", "reliability"}
                        else ChangeRisk.MEDIUM
                    ),
                    prerequisites=(f"baseline:{signal.baseline:.6g}",),
                )
            )
        if not recommendations and run.results:
            recommendations.append(
                OptimizationRecommendation.new(
                    kind=ImprovementKind.QUALITY_OPTIMIZATION,
                    target=ImprovementTarget.AGENT,
                    rationale=(
                        "No failure or regression signal is present; propose a measured quality "
                        "experiment rather than an uncontrolled change."
                    ),
                    expected_benefit={"quality": 0.01},
                    confidence=0.55,
                    risk=ChangeRisk.LOW,
                )
            )
        return tuple(recommendations[:32])

    def analyze(
        self,
        run: EvaluationRun,
        *,
        baseline: Mapping[str, float] | None = None,
        thresholds: Mapping[str, float] | None = None,
        dimensions: Mapping[str, float] | None = None,
    ) -> ImprovementReport:
        if not run.results:
            raise ImprovementError("cannot improve an empty run")
        _safe(run.metadata, "run metadata")
        clusters = self.cluster_failures(run)
        current = dict(
            dimensions
            or {
                "quality": run.score,
                "reliability": sum(result.reliable for result in run.results) / len(run.results),
                "security": sum(result.security_passed for result in run.results) / len(run.results),
                "cost": 1.0 / (1.0 + sum(result.cost for result in run.results)),
                "latency": 1.0 / (
                    1.0
                    + sum(result.duration_ms for result in run.results) / len(run.results) / 1000
                ),
            }
        )
        regressions = self.detect_regressions(current, baseline or {}, thresholds or {})
        recommendations = self.recommend(run, clusters, regressions)
        envelope = {
            "source_run_id": run.run_id,
            "clusters": [_cluster_dict(c) for c in clusters],
            "regressions": [_regression_dict(s) for s in regressions],
            "recommendations": [
                {
                    "id": r.recommendation_id,
                    "kind": r.kind.value,
                    "target": r.target.value,
                    "risk": r.risk.value,
                    "confidence": r.confidence,
                }
                for r in recommendations
            ],
        }
        digest = hashlib.sha256(
            json.dumps(envelope, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        report = ImprovementReport(
            f"report_{uuid.uuid4().hex}", run.run_id, tuple(clusters),
            tuple(regressions), recommendations, digest,
        )
        self.store.append("analysis", envelope)
        return report

    @staticmethod
    def assign_variant(spec: ExperimentSpec, *, subject: str, salt: str = "") -> tuple[str, int]:
        if not subject.strip() or len(subject) > 512 or len(salt) > 512:
            raise ImprovementError("invalid experiment subject")
        digest = hashlib.sha256(f"{spec.experiment_id}|{subject}|{salt}".encode()).digest()
        bucket = int.from_bytes(digest[:4], "big") % 10_000
        weights = spec.weights or tuple(1 for _ in spec.variants)
        target = bucket * sum(weights) // 10_000
        cursor = 0
        for variant, weight in zip(spec.variants, weights):
            cursor += weight
            if target < cursor:
                return variant, bucket
        raise ImprovementError("variant selection failed")

    @staticmethod
    def canary_allowed(
        policy: CanaryPolicy,
        *,
        samples: int,
        error_rate: float,
        cost_ratio: float,
        latency_ratio: float,
        quality: float,
    ) -> tuple[bool, tuple[str, ...]]:
        reasons = []
        if samples < policy.minimum_samples:
            reasons.append("insufficient canary samples")
        if error_rate > policy.maximum_error_rate:
            reasons.append("canary error rate exceeded")
        if cost_ratio > policy.maximum_cost_ratio:
            reasons.append("canary cost ratio exceeded")
        if latency_ratio > policy.maximum_latency_ratio:
            reasons.append("canary latency ratio exceeded")
        if quality < policy.minimum_quality:
            reasons.append("canary quality floor not met")
        return not reasons, tuple(reasons)

    @staticmethod
    def require_approval(
        recommendation: OptimizationRecommendation,
        approval: ApprovalRecord | None,
    ) -> bool:
        consequential = (
            recommendation.risk in {ChangeRisk.HIGH, ChangeRisk.CRITICAL}
            or recommendation.target
            in {ImprovementTarget.ROUTING, ImprovementTarget.MODEL, ImprovementTarget.WORKFLOW}
        )
        return consequential and not (
            approval
            and approval.approved
            and approval.recommendation_id == recommendation.recommendation_id
        )

    @staticmethod
    def rollback_plan(
        recommendation: OptimizationRecommendation,
        previous_version: str,
        trigger: str,
    ) -> RollbackPlan:
        if recommendation.status not in {
            RecommendationStatus.CANARY,
            RecommendationStatus.PROMOTED,
        }:
            raise ImprovementError(
                "rollback requires an active canary or promoted recommendation"
            )
        return RollbackPlan(
            f"rollback_{uuid.uuid4().hex}",
            recommendation.recommendation_id,
            previous_version,
            trigger,
        )
