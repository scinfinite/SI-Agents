from __future__ import annotations

import json
import pytest

from core.observability import LiveFeed, ObservabilityService, Severity, TelemetryStore, TraceContext


def test_telemetry_redacts_secrets_and_enforces_tenant_scope() -> None:
    store = TelemetryStore()
    record = store.append(
        kind="log", name="auth", tenant_id="t1", project_id="p1",
        payload={"token": "supersecret", "nested": {"password": "pw"}, "message": "safe"},
    )
    assert record.payload["token"] == "[REDACTED]"
    assert "supersecret" not in store.export_jsonl(tenant_id="t1", project_id="p1")
    assert store.query(tenant_id="t2", project_id="p1") == ()
    assert store.integrity(tenant_id="t1", project_id="p1")
    with pytest.raises(ValueError):
        store.append(kind="log", name="oversized", payload={"blob": "x" * 70_000})


def test_integrity_detects_tampering() -> None:
    store = TelemetryStore()
    record = store.append(kind="event", name="x", payload={"v": 1})
    store.db.execute("UPDATE telemetry SET payload_json=? WHERE record_id=?", (json.dumps({"v": 2}), record.record_id))
    assert not store.integrity()


def test_integrity_scans_beyond_query_page() -> None:
    store = TelemetryStore()
    for index in range(1001):
        store.append(kind="event", name=f"e-{index}", payload={"v": index})
    target = store.query(limit=1, offset=1000)[0]
    store.db.execute("UPDATE telemetry SET payload_json=? WHERE record_id=?", (json.dumps({"tampered": True}), target.record_id))
    assert not store.integrity()


def test_deep_redaction_and_resource_bounds() -> None:
    store = TelemetryStore()
    record = store.append(kind="event", name="nested", payload={"value": "Authorization: Bearer secret-value"})
    assert record.payload["value"] == "[REDACTED]"
    with pytest.raises(ValueError):
        store.append(kind="event", name="wide", payload={str(i): i for i in range(257)})


def test_trace_live_feed_metrics_and_health() -> None:
    store = TelemetryStore()
    feed = LiveFeed(max_records=2)
    service = ObservabilityService(store, feed=feed)
    trace = TraceContext()
    span = service.start_span("run", trace=trace)
    span.finish()
    service.log("failure", "bad", severity=Severity.ERROR)
    service.log("debug", "ok", severity=Severity.DEBUG)
    service.metrics.observe("latency", 10)
    service.metrics.observe("latency", 20)
    service.metrics.observe("latency", 30)
    assert len(feed.read()) == 2
    metric = service.metrics.snapshot("latency")
    assert metric.count == 3
    assert metric.p95 == 30
    health = service.health()
    assert health.errors == 1
    assert health.active_traces == 1
    assert health.p95_latency_ms >= 0
    assert service.timeline(trace.trace_id) != ()


def test_span_correlation_and_causation_are_preserved() -> None:
    service = ObservabilityService()
    first = service.start_span("root", correlation_id="c1")
    record = first.finish()
    assert record.correlation_id == "c1"
    second = service.start_span("child", trace=TraceContext(record.payload["trace_id"], record.payload["span_id"]), causation_id=record.record_id)
    child = second.finish()
    assert child.causation_id == record.record_id
