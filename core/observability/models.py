"""Structured observability contracts for SI Core."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import StrEnum
import uuid
from typing import Any, Mapping

class Severity(StrEnum):
    DEBUG="debug"; INFO="info"; WARNING="warning"; ERROR="error"; CRITICAL="critical"

@dataclass(frozen=True, slots=True)
class TelemetryRecord:
    record_id:str; occurred_at:float; kind:str; name:str; severity:Severity
    tenant_id:str|None; project_id:str|None; entity_type:str|None; entity_id:str|None
    correlation_id:str|None; causation_id:str|None; payload:Mapping[str,Any]; digest:str

@dataclass(frozen=True, slots=True)
class TraceContext:
    trace_id:str=field(default_factory=lambda:uuid.uuid4().hex)
    parent_span_id:str|None=None

@dataclass(frozen=True, slots=True)
class Span:
    span_id:str; trace_id:str; name:str; start_at:float; end_at:float; status:str
    attributes:Mapping[str,Any]=field(default_factory=dict)
    correlation_id:str|None=None; causation_id:str|None=None
    @property
    def duration_ms(self)->float:return max(0.0,(self.end_at-self.start_at)*1000)

@dataclass(frozen=True, slots=True)
class MetricSnapshot:
    name:str; count:int; total:float; minimum:float|None; maximum:float|None
    p50:float|None; p95:float|None; latest:float|None

@dataclass(frozen=True, slots=True)
class OperatorHealth:
    total_records:int; errors:int; error_rate:float; active_traces:int
    p95_latency_ms:float; top_error_names:tuple[tuple[str,int],...]
