"""Benchmark execution, regression, experimentation, and release gates."""
from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
import hashlib
import json
from pathlib import Path
import sqlite3
import time
import uuid

from core.security.platform import SecretScanner

from .models import (
    EvaluationDimension,
    EvaluationFailure,
    EvaluationReport,
    EvaluationRun,
    EvaluationSample,
    ExperimentAssignment,
    ExperimentSpec,
    GoldenCase,
    HumanReview,
    Regression,
    ReleaseGatePolicy,
)
from .scoring import score_case

MAX_SUITE_CASES = 10_000
MAX_PAYLOAD_BYTES = 256 * 1024


class EvaluationError(ValueError):
    """Evaluation contract violation."""


class EvaluationStore:
    def __init__(self, path: str | Path = ":memory:") -> None:
        self.db = sqlite3.connect(
            str(path),
            isolation_level=None,
            check_same_thread=False,
        )
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript(
            """CREATE TABLE IF NOT EXISTS evaluation_runs(
            run_id TEXT PRIMARY KEY,suite_id TEXT NOT NULL,version TEXT NOT NULL,
            started_at REAL NOT NULL,completed_at REAL NOT NULL,score REAL NOT NULL,
            passed INTEGER NOT NULL,payload_json TEXT NOT NULL,evidence_digest TEXT NOT NULL);
            CREATE INDEX IF NOT EXISTS ix_eval_runs ON evaluation_runs(suite_id,completed_at DESC);
            CREATE TABLE IF NOT EXISTS human_reviews(
            review_id TEXT PRIMARY KEY,run_id TEXT NOT NULL,case_id TEXT NOT NULL,
            reviewer_id TEXT NOT NULL,score REAL NOT NULL,rationale TEXT NOT NULL,
            created_at REAL NOT NULL);"""
        )

    def close(self) -> None:
        self.db.close()

    def save(self, run: EvaluationRun) -> str:
        payload = {
            "metadata": dict(run.metadata),
            "results": [
                {
                    "case_id": result.case_id,
                    "weighted_score": result.weighted_score,
                    "passed": result.passed,
                    "duration_ms": result.duration_ms,
                    "cost": result.cost,
                    "reliable": result.reliable,
                    "security_passed": result.security_passed,
                    "failure": result.failure.value if result.failure else None,
                    "scores": [
                        {
                            "metric_id": score.metric_id,
                            "score": score.score,
                            "passed": score.passed,
                            "details": score.details,
                        }
                        for score in result.scores
                    ],
                }
                for result in run.results
            ],
        }
        encoded = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        if len(encoded.encode()) > MAX_PAYLOAD_BYTES:
            raise EvaluationError("evaluation payload exceeds limit")
        digest = hashlib.sha256(encoded.encode()).hexdigest()
        self.db.execute(
            "INSERT INTO evaluation_runs VALUES(?,?,?,?,?,?,?,?,?)",
            (
                run.run_id,
                run.suite_id,
                run.version,
                run.started_at,
                run.completed_at,
                run.score,
                int(run.passed),
                encoded,
                digest,
            ),
        )
        return digest

    def recent(self, suite_id: str, limit: int = 20) -> tuple[sqlite3.Row, ...]:
        bounded = max(1, min(limit, 100))
        return tuple(
            self.db.execute(
                "SELECT * FROM evaluation_runs WHERE suite_id=? "
                "ORDER BY completed_at DESC LIMIT ?",
                (suite_id, bounded),
            ).fetchall()
        )

    def record_review(self, review: HumanReview) -> None:
        self.db.execute(
            "INSERT INTO human_reviews VALUES(?,?,?,?,?,?,?)",
            (
                review.review_id,
                review.run_id,
                review.case_id,
                review.reviewer_id,
                review.score,
                review.rationale,
                review.created_at,
            ),
        )

    def review_average(self, run_id: str, case_id: str) -> float | None:
        row = self.db.execute(
            "SELECT AVG(score) AS score FROM human_reviews WHERE run_id=? AND case_id=?",
            (run_id, case_id),
        ).fetchone()
        return float(row["score"]) if row and row["score"] is not None else None


class BenchmarkEngine:
    def __init__(self, store: EvaluationStore | None = None) -> None:
        self.store = store or EvaluationStore()

    def run(
        self,
        *,
        suite_id: str,
        version: str,
        cases: Iterable[GoldenCase],
        evaluator: Callable[[object], EvaluationSample],
        metadata: Mapping[str, object] | None = None,
    ) -> EvaluationRun:
        selected = tuple(cases)
        if not 0 < len(selected) <= MAX_SUITE_CASES:
            raise EvaluationError("invalid suite size")
        seen: set[str] = set()
        for case in selected:
            if case.case_id in seen:
                raise EvaluationError("duplicate case id")
            seen.add(case.case_id)
            for value in (case.input, case.expected, case.metadata):
                serialized = json.dumps(value, default=str, ensure_ascii=False)
                if SecretScanner.contains_secret(serialized):
                    raise EvaluationError(
                        f"secret-like evaluation data in {case.case_id}"
                    )
        started = time.time()
        results = []
        for case in selected:
            try:
                sample = evaluator(case.input)
            except TimeoutError:
                sample = EvaluationSample(
                    case.case_id,
                    None,
                    failure=EvaluationFailure.TIMEOUT,
                    reliable=False,
                )
            except PermissionError:
                sample = EvaluationSample(
                    case.case_id,
                    None,
                    failure=EvaluationFailure.AUTHORIZATION,
                    reliable=False,
                )
            except Exception:
                sample = EvaluationSample(
                    case.case_id,
                    None,
                    failure=EvaluationFailure.UNKNOWN,
                    reliable=False,
                )
            if sample.case_id != case.case_id:
                raise EvaluationError("evaluator returned wrong case")
            results.append(score_case(case, sample=sample))
        run = EvaluationRun(
            f"eval_{uuid.uuid4().hex}",
            suite_id,
            version,
            started,
            time.time(),
            tuple(results),
            dict(metadata or {}),
        )
        self.store.save(run)
        return run

    @staticmethod
    def regressions(
        current: Mapping[str, float],
        baseline: Mapping[str, float],
        thresholds: Mapping[str, float],
    ) -> tuple[Regression, ...]:
        output = []
        for name, baseline_value in baseline.items():
            try:
                dimension = EvaluationDimension(name)
            except ValueError:
                continue
            now = float(current.get(name, 0.0))
            threshold = max(0.0, float(thresholds.get(name, 0.0)))
            delta = now - float(baseline_value)
            output.append(
                Regression(
                    dimension,
                    now,
                    float(baseline_value),
                    delta,
                    threshold,
                    delta < -threshold,
                )
            )
        return tuple(output)

    def report(
        self,
        run: EvaluationRun,
        *,
        baseline: Mapping[str, float] | None = None,
        thresholds: Mapping[str, float] | None = None,
        dimensions: Mapping[str, float] | None = None,
    ) -> EvaluationReport:
        count = len(run.results)
        pass_rate = sum(result.passed for result in run.results) / count
        security_rate = sum(
            result.security_passed for result in run.results
        ) / count
        reliability_rate = sum(
            result.reliable for result in run.results
        ) / count
        mean_latency = (
            sum(result.duration_ms for result in run.results) / count
        )
        total_cost = sum(result.cost for result in run.results)
        derived = {
            "quality": run.score,
            "reliability": reliability_rate,
            "security": security_rate,
            "cost": 1.0 / (1.0 + total_cost),
            "latency": 1.0 / (1.0 + mean_latency / 1000.0),
        }
        dims = dict(dimensions or derived)
        regressions = self.regressions(
            dims,
            baseline or {},
            thresholds or {},
        )
        summary = {
            "pass_rate": pass_rate,
            "security_rate": security_rate,
            "reliability_rate": reliability_rate,
            "cost_total": total_cost,
            "latency_mean_ms": mean_latency,
            "failure_counts": {
                failure.value: sum(
                    result.failure is failure for result in run.results
                )
                for failure in EvaluationFailure
            },
        }
        envelope = {
            "run_id": run.run_id,
            "suite_id": run.suite_id,
            "version": run.version,
            "dimensions": dims,
            "summary": summary,
            "regressions": [
                {
                    "dimension": regression.dimension.value,
                    "current": regression.current,
                    "baseline": regression.baseline,
                    "delta": regression.delta,
                    "threshold": regression.threshold,
                    "detected": regression.detected,
                }
                for regression in regressions
            ],
        }
        digest = hashlib.sha256(
            json.dumps(
                envelope,
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
        ).hexdigest()
        passed = run.passed and not any(
            regression.detected for regression in regressions
        )
        return EvaluationReport(
            run.run_id,
            run.suite_id,
            run.version,
            run.score,
            passed,
            count,
            regressions,
            dims,
            summary,
            digest,
        )

    @staticmethod
    def assign_variant(
        spec: ExperimentSpec,
        *,
        subject: str,
        salt: str = "",
    ) -> ExperimentAssignment:
        if not subject.strip():
            raise EvaluationError("experiment subject is required")
        digest = hashlib.sha256(
            f"{spec.experiment_id}|{subject}|{salt}".encode()
        ).digest()
        bucket = int.from_bytes(digest[:4], "big") % 10_000
        weights = spec.weights or tuple(1 for _ in spec.variants)
        target = bucket * sum(weights) // 10_000
        cursor = 0
        for index, weight in enumerate(weights):
            cursor += weight
            if target < cursor:
                return ExperimentAssignment(
                    spec.experiment_id,
                    subject,
                    spec.variants[index],
                    bucket,
                )
        raise EvaluationError("variant selection failed")

    @staticmethod
    def release_gate(
        report: EvaluationReport,
        policy: ReleaseGatePolicy | None = None,
    ) -> tuple[bool, tuple[str, ...]]:
        policy = policy or ReleaseGatePolicy()
        reasons: list[str] = []
        if report.score < policy.minimum_score:
            reasons.append("minimum score not met")
        for dimension, minimum in policy.minimum_dimensions.items():
            if float(report.dimensions.get(dimension, 0.0)) < float(minimum):
                reasons.append(f"minimum dimension not met: {dimension}")
        if sum(regression.detected for regression in report.regressions) > policy.max_regressions:
            reasons.append("regression budget exceeded")
        if report.case_count == 0:
            reasons.append("empty evaluation suite")
        return not reasons, tuple(reasons)
