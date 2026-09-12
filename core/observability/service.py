"""Operator-facing observability services."""
from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Mapping
from dataclasses import dataclass
import time
import uuid

from .models import (
    MetricSnapshot,
    OperatorHealth,
    Severity,
    TelemetryRecord,
    TraceContext,
)
from .store import TelemetryStore


class LiveFeed:
    def __init__(self, max_records: int = 500) -> None:
        if max_records <= 0:
            raise ValueError("max_records must be positive")
        self._records: deque[TelemetryRecord] = deque(maxlen=max_records)
        self._max = max_records

    def publish(self, record: TelemetryRecord) -> None:
        self._records.append(record)

    def read(self, limit: int = 100) -> tuple[TelemetryRecord, ...]:
        return tuple(list(self._records)[-max(1, min(limit, self._max)) :])

    def clear(self) -> None:
        self._records.clear()


class MetricRegistry:
    def __init__(self, store: TelemetryStore) -> None:
        self.store = store

    def observe(self, name: str, value: float, **context: object) -> TelemetryRecord:
        metric_kind = context.pop("kind", "histogram")
        payload = {"value": float(value), "metric_kind": metric_kind, **context}
        return self.store.append(kind="metric", name=name, payload=payload)

    def counter(
        self, name: str, delta: float = 1, **context: object
    ) -> TelemetryRecord:
        return self.observe(name, delta, kind="counter", **context)

    def gauge(self, name: str, value: float, **context: object) -> TelemetryRecord:
        return self.observe(name, value, kind="gauge", **context)

    def snapshot(
        self,
        name: str,
        *,
        tenant_id: str | None = None,
        project_id: str | None = None,
    ) -> MetricSnapshot:
        records = self.store.query(
            tenant_id=tenant_id,
            project_id=project_id,
            kind="metric",
            name=name,
            limit=1000,
        )
        values = sorted(
            float(record.payload["value"])
            for record in records
            if isinstance(record.payload.get("value"), (int, float))
        )
        if not values:
            return MetricSnapshot(name, 0, 0.0, None, None, None, None, None)

        def percentile(p: float) -> float:
            index = min(
                len(values) - 1,
                max(0, int((len(values) - 1) * p + 0.999999)),
            )
            return values[index]

        return MetricSnapshot(
            name,
            len(values),
            sum(values),
            values[0],
            values[-1],
            percentile(0.50),
            percentile(0.95),
            values[-1],
        )


class ObservabilityService:
    def __init__(
        self,
        store: TelemetryStore | None = None,
        *,
        feed: LiveFeed | None = None,
    ) -> None:
        self.store = store or TelemetryStore()
        self.feed = feed or LiveFeed()
        self.metrics = MetricRegistry(self.store)

    def record(self, **kwargs: object) -> TelemetryRecord:
        record = self.store.append(**kwargs)
        self.feed.publish(record)
        return record

    def log(
        self,
        name: str,
        message: str,
        *,
        severity: Severity = Severity.INFO,
        **context: object,
    ) -> TelemetryRecord:
        return self.record(
            kind="log",
            name=name,
            severity=severity,
            payload={"message": message},
            **context,
        )

    def event(
        self,
        name: str,
        *,
        payload: Mapping[str, object] | None = None,
        **context: object,
    ) -> TelemetryRecord:
        return self.record(
            kind="event",
            name=name,
            payload=payload or {},
            **context,
        )

    def start_span(
        self,
        name: str,
        *,
        trace: TraceContext | None = None,
        attributes: Mapping[str, object] | None = None,
        correlation_id: str | None = None,
        causation_id: str | None = None,
    ) -> "_SpanHandle":
        context = trace or TraceContext()
        return _SpanHandle(
            self,
            name,
            context.trace_id,
            uuid.uuid4().hex,
            time.time(),
            attributes or {},
            correlation_id,
            causation_id,
        )

    def timeline(
        self,
        trace_id: str,
        *,
        tenant_id: str | None = None,
        project_id: str | None = None,
    ) -> tuple[TelemetryRecord, ...]:
        return self.store.query(
            tenant_id=tenant_id,
            project_id=project_id,
            correlation_id=trace_id,
            limit=1000,
        )

    def health(
        self,
        *,
        tenant_id: str | None = None,
        project_id: str | None = None,
    ) -> OperatorHealth:
        records = self.store.query(
            tenant_id=tenant_id,
            project_id=project_id,
            limit=1000,
        )
        errors = sum(
            record.severity in {Severity.ERROR, Severity.CRITICAL}
            for record in records
        )
        latency = sorted(
            float(record.payload["duration_ms"])
            for record in records
            if record.kind == "span"
            and isinstance(record.payload.get("duration_ms"), (int, float))
        )
        if latency:
            p95 = latency[min(len(latency) - 1, int(0.95 * (len(latency) - 1)))]
        else:
            p95 = 0.0
        error_names: defaultdict[str, int] = defaultdict(int)
        for record in records:
            if record.severity in {Severity.ERROR, Severity.CRITICAL}:
                error_names[record.name] += 1
        traces = {
            record.payload.get("trace_id")
            for record in records
            if record.kind == "span" and record.payload.get("trace_id")
        }
        top_errors = tuple(
            sorted(error_names.items(), key=lambda item: (-item[1], item[0]))[:10]
        )
        return OperatorHealth(
            len(records),
            errors,
            errors / len(records) if records else 0.0,
            len(traces),
            p95,
            top_errors,
        )

    def export(self, **scope: str | None) -> str:
        return self.store.export_jsonl(**scope)


@dataclass
class _SpanHandle:
    service: ObservabilityService
    name: str
    trace_id: str
    span_id: str
    started: float
    attributes: Mapping[str, object]
    correlation_id: str | None
    causation_id: str | None

    def finish(
        self,
        status: str = "ok",
        attributes: Mapping[str, object] | None = None,
    ) -> TelemetryRecord:
        merged = {**self.attributes, **(attributes or {})}
        payload = {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "duration_ms": max(0.0, (time.time() - self.started) * 1000),
            "status": status,
            "attributes": merged,
        }
        return self.service.record(
            kind="span",
            name=self.name,
            payload=payload,
            correlation_id=self.correlation_id or self.trace_id,
            causation_id=self.causation_id,
        )
