"""Operator-facing observability services."""
from __future__ import annotations
from collections import defaultdict,deque
from dataclasses import dataclass
import time,uuid
from collections.abc import Mapping
from .models import MetricSnapshot,OperatorHealth,Severity,TelemetryRecord,TraceContext
from .store import TelemetryStore

class LiveFeed:
    def __init__(self,max_records:int=500):
        if max_records<=0:raise ValueError("max_records must be positive")
        self._records=deque(maxlen=max_records); self._max=max_records
    def publish(self,record:TelemetryRecord)->None:self._records.append(record)
    def read(self,limit:int=100)->tuple[TelemetryRecord,...]:
        return tuple(list(self._records)[-max(1,min(limit,self._max)):])
    def clear(self)->None:self._records.clear()

class MetricRegistry:
    def __init__(self,store:TelemetryStore):self.store=store
    def observe(self,name:str,value:float,**ctx:object)->TelemetryRecord:
        return self.store.append(kind="metric",name=name,payload={"value":float(value),"metric_kind":ctx.pop("kind","histogram"),**ctx})
    def counter(self,name:str,delta:float=1,**ctx:object)->TelemetryRecord:return self.observe(name,delta,kind="counter",**ctx)
    def gauge(self,name:str,value:float,**ctx:object)->TelemetryRecord:return self.observe(name,value,kind="gauge",**ctx)
    def snapshot(self,name:str,*,tenant_id:str|None=None,project_id:str|None=None)->MetricSnapshot:
        rows=self.store.query(tenant_id=tenant_id,project_id=project_id,kind="metric",name=name,limit=1000)
        values=sorted(float(row.payload["value"]) for row in rows if isinstance(row.payload.get("value"),(int,float)))
        if not values:return MetricSnapshot(name,0,0.0,None,None,None,None,None)
        def percentile(p:float)->float:return values[min(len(values)-1,max(0,int((len(values)-1)*p+0.999999)))]
        return MetricSnapshot(name,len(values),sum(values),values[0],values[-1],percentile(.5),percentile(.95),values[-1])

class ObservabilityService:
    def __init__(self,store:TelemetryStore|None=None,*,feed:LiveFeed|None=None):
        self.store=store or TelemetryStore(); self.feed=feed or LiveFeed(); self.metrics=MetricRegistry(self.store)
    def record(self,**kwargs:object)->TelemetryRecord:
        record=self.store.append(**kwargs); self.feed.publish(record); return record
    def log(self,name:str,message:str,*,severity:Severity=Severity.INFO,**ctx:object)->TelemetryRecord:
        return self.record(kind="log",name=name,severity=severity,payload={"message":message},**ctx)
    def event(self,name:str,*,payload:Mapping[str,object]|None=None,**ctx:object)->TelemetryRecord:
        return self.record(kind="event",name=name,payload=payload or {},**ctx)
    def start_span(self,name:str,*,trace:TraceContext|None=None,attributes:Mapping[str,object]|None=None,
                   correlation_id:str|None=None,causation_id:str|None=None)->"_SpanHandle":
        context=trace or TraceContext(); return _SpanHandle(self,name,context.trace_id,
            uuid.uuid4().hex,time.time(),attributes or {},correlation_id,causation_id)
    def timeline(self,trace_id:str,*,tenant_id:str|None=None,project_id:str|None=None)->tuple[TelemetryRecord,...]:
        return self.store.query(tenant_id=tenant_id,project_id=project_id,correlation_id=trace_id,limit=1000)
    def health(self,*,tenant_id:str|None=None,project_id:str|None=None)->OperatorHealth:
        rows=self.store.query(tenant_id=tenant_id,project_id=project_id,limit=1000)
        errors=sum(row.severity in {Severity.ERROR,Severity.CRITICAL} for row in rows)
        lat=sorted(float(row.payload["duration_ms"]) for row in rows if row.kind=="span" and isinstance(row.payload.get("duration_ms"),(int,float)))
        p95=lat[min(len(lat)-1,int(.95*(len(lat)-1)))] if lat else 0.0
        counts=defaultdict(int)
        for row in rows:
            if row.severity in {Severity.ERROR,Severity.CRITICAL}:counts[row.name]+=1
        traces={row.payload.get("trace_id") for row in rows if row.kind=="span" and row.payload.get("trace_id")}
        return OperatorHealth(len(rows),errors,errors/len(rows) if rows else 0.0,len(traces),p95,
                              tuple(sorted(counts.items(),key=lambda x:(-x[1],x[0]))[:10]))
    def export(self,**scope:str|None)->str:return self.store.export_jsonl(**scope)

@dataclass
class _SpanHandle:
    service:ObservabilityService; name:str; trace_id:str; span_id:str; started:float
    attributes:Mapping[str,object]; correlation_id:str|None; causation_id:str|None
    def finish(self,status:str="ok",attributes:Mapping[str,object]|None=None)->TelemetryRecord:
        merged={**self.attributes,**(attributes or {})}
        payload={"trace_id":self.trace_id,"span_id":self.span_id,
                 "duration_ms":max(0.0,(time.time()-self.started)*1000),
                 "status":status,"attributes":merged}
        return self.service.record(kind="span",name=self.name,payload=payload,
                                   correlation_id=self.correlation_id or self.trace_id,
                                   causation_id=self.causation_id)
