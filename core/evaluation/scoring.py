"""Deterministic benchmark scoring functions."""
from __future__ import annotations

import json
import re
from typing import Any

from .models import CaseResult, EvaluationSample, GoldenCase, MetricKind, MetricScore


def _normalized(value: Any) -> str:
    return " ".join(str(value).split()).casefold()


def score_metric(case: GoldenCase, metric_id: str, actual: Any) -> MetricScore:
    metric = next(
        (candidate for candidate in case.metrics if candidate.metric_id == metric_id),
        None,
    )
    if metric is None:
        raise KeyError(metric_id)
    target = case.expected if metric.target is None else metric.target
    score = 0.0
    details = ""
    try:
        if metric.kind is MetricKind.EXACT:
            score = float(actual == target)
        elif metric.kind is MetricKind.NORMALIZED:
            score = float(_normalized(actual) == _normalized(target))
        elif metric.kind is MetricKind.CONTAINS:
            score = float(_normalized(target) in _normalized(actual))
        elif metric.kind is MetricKind.JSON_EQUAL:
            score = float(
                json.loads(_normalized(actual)) == json.loads(_normalized(target))
            )
        elif metric.kind is MetricKind.NUMERIC_ABS:
            delta = abs(float(actual) - float(target))
            tolerance = float(metric.tolerance)
            score = 1.0 if delta <= tolerance else max(0.0, 1.0 - delta / tolerance)
            details = f"abs_delta={delta:g}"
        elif metric.kind is MetricKind.RUBRIC:
            if isinstance(actual, (int, float)):
                score = max(0.0, min(1.0, float(actual)))
            else:
                match = re.search(
                    r"(?:score|rating)\s*[:=]\s*(0(?:\.\d+)?|1(?:\.0+)?)",
                    str(actual),
                    re.IGNORECASE,
                )
                score = float(match.group(1)) if match else 0.0
    except (TypeError, ValueError, json.JSONDecodeError):
        score = 0.0
    passed = score >= metric.threshold
    return MetricScore(metric.metric_id, score, passed, details)


def score_case(case: GoldenCase, *, sample: "EvaluationSample") -> "CaseResult":
    from .models import EvaluationFailure

    scores = tuple(score_metric(case, metric.metric_id, sample.actual) for metric in case.metrics)
    total_weight = sum(metric.weight for metric in case.metrics)
    weights = {metric.metric_id: metric.weight for metric in case.metrics}
    weighted = sum(score.score * weights[score.metric_id] for score in scores) / total_weight
    blocked = (
        not sample.passed_security
        or not sample.reliable
        or sample.failure is not None
        or any(not score.passed for score in scores)
    )
    if blocked:
        weighted = 0.0
    failure = sample.failure
    if failure is None and not sample.passed_security:
        failure = EvaluationFailure.SECURITY_VIOLATION
    return CaseResult(
        case.case_id,
        scores,
        weighted,
        not blocked,
        sample.duration_ms,
        sample.cost,
        sample.reliable and sample.failure is None,
        sample.passed_security,
        failure,
    )
