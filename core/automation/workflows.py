"""Governed workflow automation for Phase 65.

Definitions are declarative; registered callables are execution adapters. Persisted
state contains only JSON-safe workflow data and never callable objects or secrets.
"""
from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from hashlib import sha256
from pathlib import Path
from threading import RLock
from uuid import uuid4

_MAX_STEPS = 256
_MAX_FANOUT = 256
_MAX_LOOP = 64
_MAX_RETRIES = 8
_MAX_PAYLOAD_BYTES = 256 * 1024
_MAX_RUNS = 10_000


class WorkflowStepKind(StrEnum):
    TASK = "task"
    CONDITION = "condition"
    WAIT = "wait"
    HUMAN = "human"
    FANOUT = "fanout"
    LOOP = "loop"
    DELEGATE = "delegate"
    COMPENSATE = "compensate"


class WorkflowRunStatus(StrEnum):
    RUNNING = "running"
    WAITING = "waiting"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TriggerKind(StrEnum):
    MANUAL = "manual"
    EVENT = "event"
    INTERVAL = "interval"
    WEBHOOK = "webhook"


@dataclass(frozen=True)
class WorkflowTrigger:
    kind: TriggerKind
    name: str
    interval_seconds: int | None = None

    def __post_init__(self) -> None:
        if not self.name.strip() or len(self.name) > 128:
            raise ValueError("trigger name is required and bounded")
        if self.kind is TriggerKind.INTERVAL:
            if not 1 <= (self.interval_seconds or 0) <= 31_536_000:
                raise ValueError("interval trigger must be between one second and one year")
        elif self.interval_seconds is not None:
            raise ValueError("only interval triggers accept interval_seconds")


@dataclass(frozen=True)
class WorkflowStep:
    id: str
    kind: WorkflowStepKind
    action: str | None = None
    depends_on: tuple[str, ...] = ()
    condition: str | None = None
    items_key: str | None = None
    wait_seconds: int | None = None
    approval_key: str | None = None
    max_iterations: int = 1
    retry_attempts: int = 1
    compensation_action: str | None = None
    delegate_to: str | None = None

    def __post_init__(self) -> None:
        if not self.id or len(self.id) > 128 or self.id != self.id.strip():
            raise ValueError("invalid workflow step id")
        if len(self.depends_on) > _MAX_STEPS or len(set(self.depends_on)) != len(self.depends_on):
            raise ValueError("workflow dependencies must be unique and bounded")
        if self.id in self.depends_on:
            raise ValueError("workflow step cannot depend on itself")
        if not 1 <= self.retry_attempts <= _MAX_RETRIES:
            raise ValueError("retry_attempts is out of bounds")
        if not 1 <= self.max_iterations <= _MAX_LOOP:
            raise ValueError("max_iterations is out of bounds")
        if self.wait_seconds is not None and not 1 <= self.wait_seconds <= 31_536_000:
            raise ValueError("wait_seconds is out of bounds")
        if self.kind is WorkflowStepKind.WAIT and self.wait_seconds is None:
            raise ValueError("wait step requires wait_seconds")
        if self.kind is WorkflowStepKind.HUMAN and not self.approval_key:
            raise ValueError("human step requires approval_key")
        if self.kind in {WorkflowStepKind.TASK, WorkflowStepKind.FANOUT, WorkflowStepKind.LOOP, WorkflowStepKind.DELEGATE} and not self.action:
            raise ValueError("executable workflow step requires action")
        if self.kind is WorkflowStepKind.CONDITION and not self.condition:
            raise ValueError("condition step requires condition")


@dataclass(frozen=True)
class WorkflowDefinition:
    workflow_id: str
    version: int
    name: str
    steps: tuple[WorkflowStep, ...]
    triggers: tuple[WorkflowTrigger, ...] = ()
    max_runtime_seconds: int = 86_400
    template: str | None = None

    def __post_init__(self) -> None:
        if not self.workflow_id.strip() or not self.name.strip():
            raise ValueError("workflow_id and name are required")
        if self.version < 1 or not self.steps or len(self.steps) > _MAX_STEPS:
            raise ValueError("workflow version/step count is invalid")
        if not 1 <= self.max_runtime_seconds <= 31_536_000:
            raise ValueError("max_runtime_seconds is out of bounds")
        ids = {step.id for step in self.steps}
        if len(ids) != len(self.steps):
            raise ValueError("workflow has duplicate step ids")
        for step in self.steps:
            if any(dep not in ids for dep in step.depends_on):
                raise ValueError(f"unknown dependency in step {step.id}")
        _topological(self.steps)

    def fingerprint(self) -> str:
        raw = json.dumps(self.as_dict(), sort_keys=True, separators=(",", ":"))
        return "sha256:" + sha256(raw.encode()).hexdigest()

    def as_dict(self) -> dict[str, object]:
        return _jsonable(asdict(self))  # type: ignore[return-value]


@dataclass
class WorkflowRun:
    run_id: str
    workflow_id: str
    version: int
    definition_fingerprint: str
    status: WorkflowRunStatus
    subject: str
    variables: dict[str, object]
    step_states: dict[str, str] = field(default_factory=dict)
    step_results: dict[str, object] = field(default_factory=dict)
    attempts: dict[str, int] = field(default_factory=dict)
    completed_steps: list[str] = field(default_factory=list)
    wait_until: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    error: str | None = None
    trigger: str = "manual"

    def as_dict(self) -> dict[str, object]:
        return _jsonable(asdict(self))  # type: ignore[return-value]


Adapter = Callable[[object], object]


class WorkflowEngine:
    """Durable, bounded workflow state machine with explicit adapter registration."""

    def __init__(self, *, state_path: str | Path | None = None) -> None:
        self.state_path = Path(state_path) if state_path else None
        self._lock = RLock()
        self._definitions: dict[tuple[str, int], WorkflowDefinition] = {}
        self._templates: dict[str, WorkflowDefinition] = {}
        self._runs: dict[str, WorkflowRun] = {}
        self._idempotency: dict[str, tuple[str, str]] = {}
        self._actions: dict[str, Adapter] = {}
        self._conditions: dict[str, Callable[[dict[str, object]], bool]] = {}
        self._delegates: dict[str, Callable[[dict[str, object]], object]] = {}
        self._load()

    def register(self, definition: WorkflowDefinition) -> None:
        with self._lock:
            key = (definition.workflow_id, definition.version)
            if key in self._definitions:
                raise ValueError("workflow version already registered")
            self._definitions[key] = definition
            self._persist()

    def register_template(self, name: str, definition: WorkflowDefinition) -> None:
        name = _name(name)
        with self._lock:
            if name in self._templates:
                raise ValueError("template already registered")
            self._templates[name] = definition
            self._persist()

    def instantiate(self, template: str, workflow_id: str, version: int = 1) -> WorkflowDefinition:
        with self._lock:
            base = self._templates.get(template)
        if base is None:
            raise KeyError(template)
        definition = WorkflowDefinition(workflow_id, version, base.name, base.steps, base.triggers, base.max_runtime_seconds, template)
        self.register(definition)
        return definition

    def register_action(self, name: str, action: Adapter) -> None:
        self._actions[_name(name)] = action

    def register_condition(self, name: str, condition: Callable[[dict[str, object]], bool]) -> None:
        self._conditions[_name(name)] = condition

    def register_delegate(self, name: str, delegate: Callable[[dict[str, object]], object]) -> None:
        self._delegates[_name(name)] = delegate

    def start(self, workflow_id: str, *, version: int | None = None, subject: str = "", variables: dict[str, object] | None = None, idempotency_key: str | None = None, trigger: str = "manual") -> WorkflowRun:
        definition = self.definition(workflow_id, version)
        subject = _bounded_text(subject, "subject", 512)
        variables = _safe_json(variables or {})
        key = _bounded_text(idempotency_key, "idempotency key", 256) if idempotency_key is not None else None
        request_fingerprint = sha256(json.dumps({"workflow": definition.workflow_id, "version": definition.version, "subject": subject, "variables": variables, "trigger": trigger}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        with self._lock:
            if key:
                existing = self._idempotency.get(key)
                if existing:
                    run_id, fingerprint = existing
                    if fingerprint != request_fingerprint:
                        raise ValueError("idempotency key was already used for a different request")
                    return self._runs[run_id]
            if len(self._runs) >= _MAX_RUNS:
                self._compact_runs()
            run = WorkflowRun(uuid4().hex, definition.workflow_id, definition.version, definition.fingerprint(), WorkflowRunStatus.RUNNING, subject, variables, {step.id: "pending" for step in definition.steps}, trigger=trigger)
            self._runs[run.run_id] = run
            if key:
                self._idempotency[key] = (run.run_id, request_fingerprint)
            self._persist()
            return run

    def definition(self, workflow_id: str, version: int | None = None) -> WorkflowDefinition:
        with self._lock:
            if version is None:
                candidates = [item for (wid, _), item in self._definitions.items() if wid == workflow_id]
                if not candidates:
                    raise KeyError(workflow_id)
                return max(candidates, key=lambda item: item.version)
            try:
                return self._definitions[(workflow_id, version)]
            except KeyError:
                raise KeyError(f"{workflow_id}@{version}") from None

    def tick(self, run_id: str, *, now: datetime | None = None) -> WorkflowRun:
        now = _utc(now or datetime.now(UTC))
        with self._lock:
            run = self._runs[run_id]
            definition = self.definition(run.workflow_id, run.version)
            if run.status in {WorkflowRunStatus.SUCCEEDED, WorkflowRunStatus.FAILED, WorkflowRunStatus.CANCELLED}:
                return run
            if now - _parse(run.created_at) > timedelta(seconds=definition.max_runtime_seconds):
                return self._fail(run, "workflow runtime exceeded")
            if run.status is WorkflowRunStatus.WAITING:
                if run.wait_until and _parse(run.wait_until) > now:
                    return run
                waiting_step = next((s for s in definition.steps if run.step_states[s.id] == "waiting" and s.kind is WorkflowStepKind.WAIT), None)
                if waiting_step:
                    run.step_states[waiting_step.id] = "pending"
                    run.wait_until = None
                elif any(s.kind is WorkflowStepKind.HUMAN and run.step_states[s.id] == "waiting" for s in definition.steps):
                    for step in definition.steps:
                        if step.kind is WorkflowStepKind.HUMAN and run.step_states[step.id] == "waiting" and run.variables.get(step.approval_key or "") is True:
                            run.step_states[step.id] = "pending"
                    if not any(s.kind is WorkflowStepKind.HUMAN and run.step_states[s.id] == "waiting" for s in definition.steps):
                        run.wait_until = None
                    else:
                        return run
                run.status = WorkflowRunStatus.RUNNING
            progressed = True
            while progressed and run.status is WorkflowRunStatus.RUNNING:
                progressed = False
                for step in definition.steps:
                    if run.step_states[step.id] != "pending":
                        continue
                    dep_states = [run.step_states[d] for d in step.depends_on]
                    if any(state == "skipped" for state in dep_states):
                        run.step_states[step.id] = "skipped"
                        progressed = True
                        continue
                    if not all(state == "succeeded" for state in dep_states):
                        continue
                    if step.condition:
                        condition = self._conditions.get(step.condition)
                        if condition is None:
                            return self._fail(run, f"condition is not registered: {step.condition}")
                        if not bool(condition(run.variables)):
                            run.step_states[step.id] = "skipped"
                            progressed = True
                            continue
                    changed = self._execute_step(run, step, now)
                    progressed = progressed or changed
                    if run.status is not WorkflowRunStatus.RUNNING:
                        break
            if all(state in {"succeeded", "skipped"} for state in run.step_states.values()):
                run.status = WorkflowRunStatus.SUCCEEDED
            run.updated_at = now.isoformat()
            self._persist()
            return run

    def cancel(self, run_id: str, reason: str = "cancelled") -> WorkflowRun:
        with self._lock:
            run = self._runs[run_id]
            if run.status in {WorkflowRunStatus.SUCCEEDED, WorkflowRunStatus.FAILED, WorkflowRunStatus.CANCELLED}:
                return run
            run.status = WorkflowRunStatus.CANCELLED
            run.error = _bounded_text(reason, "reason", 512)
            self._persist()
            return run

    def resume(self, run_id: str, *, variables: dict[str, object] | None = None, now: datetime | None = None) -> WorkflowRun:
        with self._lock:
            run = self._runs[run_id]
            if run.status not in {WorkflowRunStatus.WAITING, WorkflowRunStatus.RUNNING}:
                raise ValueError("only waiting or running workflows can resume")
            if variables:
                run.variables.update(_safe_json(variables))
        return self.tick(run_id, now=now)

    def event(self, event_name: str, payload: dict[str, object], *, subject: str = "", now: datetime | None = None) -> tuple[WorkflowRun, ...]:
        return self._triggered(TriggerKind.EVENT, event_name, payload, subject=subject, now=now)

    def webhook(self, hook_name: str, payload: dict[str, object], *, subject: str = "", now: datetime | None = None) -> tuple[WorkflowRun, ...]:
        return self._triggered(TriggerKind.WEBHOOK, hook_name, payload, subject=subject, now=now)

    def due_intervals(self, *, now: datetime | None = None) -> tuple[WorkflowDefinition, ...]:
        now = _utc(now or datetime.now(UTC))
        due: list[WorkflowDefinition] = []
        for definition in self._definitions.values():
            intervals = [t.interval_seconds for t in definition.triggers if t.kind is TriggerKind.INTERVAL and t.interval_seconds]
            if not intervals:
                continue
            latest = max((r for r in self._runs.values() if r.workflow_id == definition.workflow_id and r.version == definition.version), key=lambda r: r.created_at, default=None)
            if latest is None or any(now - _parse(latest.created_at) >= timedelta(seconds=interval) for interval in intervals):
                due.append(definition)
        return tuple(due)

    def trigger_intervals(self, *, now: datetime | None = None) -> tuple[WorkflowRun, ...]:
        now = _utc(now or datetime.now(UTC))
        started = []
        for definition in self.due_intervals(now=now):
            started.append(self.start(definition.workflow_id, version=definition.version, variables={"trigger": {"kind": "interval", "at": now.isoformat()}}, trigger="interval"))
        return tuple(started)

    def run(self, run_id: str) -> WorkflowRun:
        with self._lock:
            return self._runs[run_id]

    def list_runs(self, *, status: WorkflowRunStatus | None = None, limit: int = 100) -> tuple[WorkflowRun, ...]:
        if not 1 <= limit <= 500:
            raise ValueError("limit must be between 1 and 500")
        with self._lock:
            runs = tuple(self._runs.values())
        if status is not None:
            runs = tuple(item for item in runs if item.status is status)
        return tuple(sorted(runs, key=lambda item: item.created_at, reverse=True)[:limit])

    def _triggered(self, kind: TriggerKind, name: str, payload: dict[str, object], *, subject: str, now: datetime | None) -> tuple[WorkflowRun, ...]:
        payload = _safe_json(payload)
        started = []
        for definition in tuple(self._definitions.values()):
            if any(t.kind is kind and t.name == name for t in definition.triggers):
                started.append(self.start(definition.workflow_id, version=definition.version, subject=subject, variables={"trigger": payload}, trigger=name))
        if now is not None:
            for run in started:
                run.updated_at = _utc(now).isoformat()
        return tuple(started)

    def _execute_step(self, run: WorkflowRun, step: WorkflowStep, now: datetime) -> bool:
        if step.kind is WorkflowStepKind.CONDITION:
            condition = self._conditions.get(step.condition or "")
            if condition is None:
                return self._fail(run, f"condition is not registered: {step.condition}") is run
            result = bool(condition(run.variables))
            run.step_states[step.id] = "succeeded" if result else "skipped"
            run.variables[f"condition:{step.id}"] = result
            if result:
                run.completed_steps.append(step.id)
            return True
        if step.kind is WorkflowStepKind.WAIT:
            run.step_states[step.id] = "waiting"
            run.status = WorkflowRunStatus.WAITING
            run.wait_until = (now + timedelta(seconds=step.wait_seconds or 1)).isoformat()
            return True
        if step.kind is WorkflowStepKind.HUMAN:
            if run.variables.get(step.approval_key or "") is True:
                run.step_states[step.id] = "succeeded"
                run.completed_steps.append(step.id)
                return True
            run.step_states[step.id] = "waiting"
            run.status = WorkflowRunStatus.WAITING
            return True
        if step.kind is WorkflowStepKind.FANOUT:
            items = run.variables.get(step.items_key or "", [])
            if not isinstance(items, list) or len(items) > _MAX_FANOUT:
                return self._fail(run, "fan-out input is invalid or exceeds limit") is run
            action = self._actions.get(step.action or "")
            if action is None:
                return self._fail(run, f"action is not registered: {step.action}") is run
            try:
                results = [action(item) for item in items]
                run.step_results[step.id] = _safe_json(results)
            except Exception as exc:  # noqa: BLE001
                return self._fail(run, f"{type(exc).__name__}: {exc}") is run
            run.step_states[step.id] = "succeeded"
            run.completed_steps.append(step.id)
            return True
        if step.kind is WorkflowStepKind.LOOP:
            action = self._actions.get(step.action or "")
            condition = self._conditions.get(step.condition or "")
            if action is None or condition is None:
                return self._fail(run, "loop action/condition is not registered") is run
            results = []
            for _ in range(step.max_iterations):
                results.append(action(run.variables))
                if condition(run.variables):
                    break
            else:
                return self._fail(run, "loop iteration limit reached") is run
            run.step_results[step.id] = _safe_json(results)
            run.step_states[step.id] = "succeeded"
            run.completed_steps.append(step.id)
            return True
        if step.kind is WorkflowStepKind.DELEGATE:
            delegate = self._delegates.get(step.delegate_to or "")
            if delegate is None:
                return self._fail(run, "delegate is not registered") is run
            try:
                result = delegate(run.variables)
                run.step_results[step.id] = _safe_json(result)
            except Exception as exc:  # noqa: BLE001
                return self._fail(run, f"{type(exc).__name__}: {exc}") is run
            run.step_states[step.id] = "succeeded"
            run.completed_steps.append(step.id)
            return True
        action = self._actions.get(step.action or "")
        if action is None:
            return self._fail(run, f"action is not registered: {step.action}") is run
        for attempt in range(run.attempts.get(step.id, 0) + 1, step.retry_attempts + 1):
            run.attempts[step.id] = attempt
            try:
                result = action(run.variables)
                run.step_results[step.id] = _safe_json(result)
                run.step_states[step.id] = "succeeded"
                run.completed_steps.append(step.id)
                return True
            except Exception as exc:  # noqa: BLE001
                run.error = f"{type(exc).__name__}: {exc}"
        return self._fail(run, run.error or "step failed") is run

    def _fail(self, run: WorkflowRun, error: str) -> WorkflowRun:
        run.status = WorkflowRunStatus.FAILED
        run.error = _bounded_text(error, "error", 1024)
        definition = self.definition(run.workflow_id, run.version)
        for step_id in reversed(run.completed_steps):
            step = next(item for item in definition.steps if item.id == step_id)
            if step.compensation_action and step.compensation_action in self._actions:
                try:
                    self._actions[step.compensation_action](run.step_results.get(step_id))
                except Exception:  # noqa: BLE001
                    run.error = f"{run.error}; compensation failed for {step_id}"
        self._persist()
        return run

    def _compact_runs(self) -> None:
        finished = sorted((r for r in self._runs.values() if r.status in {WorkflowRunStatus.SUCCEEDED, WorkflowRunStatus.FAILED, WorkflowRunStatus.CANCELLED}), key=lambda item: item.created_at)
        while len(self._runs) >= _MAX_RUNS and finished:
            old = finished.pop(0)
            self._runs.pop(old.run_id, None)
            for key, value in list(self._idempotency.items()):
                if value[0] == old.run_id:
                    self._idempotency.pop(key, None)

    def _persist(self) -> None:
        if self.state_path is None:
            return
        payload = {"definitions": [item.as_dict() for item in self._definitions.values()], "templates": [item.as_dict() for item in self._templates.values()], "runs": [item.as_dict() for item in self._runs.values()], "idempotency": self._idempotency}
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        if len(encoded.encode()) > _MAX_PAYLOAD_BYTES * 4:
            raise ValueError("workflow state exceeds persistence limit")
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.state_path.with_suffix(self.state_path.suffix + ".tmp")
        temporary.write_text(encoded, encoding="utf-8")
        temporary.replace(self.state_path)

    def _load(self) -> None:
        if self.state_path is None or not self.state_path.exists():
            return
        try:
            payload = json.loads(self.state_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("invalid workflow state") from exc
        if not isinstance(payload, dict) or not isinstance(payload.get("definitions", []), list) or not isinstance(payload.get("runs", []), list):
            raise ValueError("invalid workflow state")
        for raw in payload.get("definitions", []):
            definition = _definition_from_dict(raw)
            self._definitions[(definition.workflow_id, definition.version)] = definition
        for raw in payload.get("templates", []):
            definition = _definition_from_dict(raw)
            self._templates[definition.template or definition.workflow_id] = definition
        for raw in payload.get("runs", []):
            run = WorkflowRun(**raw)
            run.status = WorkflowRunStatus(run.status)
            self._runs[run.run_id] = run
        for key, value in payload.get("idempotency", {}).items():
            if isinstance(value, list) and len(value) == 2:
                self._idempotency[str(key)] = (str(value[0]), str(value[1]))
            elif isinstance(value, str) and value in self._runs:
                self._idempotency[str(key)] = (value, "legacy")


def _definition_from_dict(raw: dict[str, object]) -> WorkflowDefinition:
    steps = tuple(WorkflowStep(**{**step, "kind": WorkflowStepKind(step["kind"]), "depends_on": tuple(step.get("depends_on", ()))}) for step in raw["steps"])  # type: ignore[arg-type]
    triggers = tuple(WorkflowTrigger(**{**trigger, "kind": TriggerKind(trigger["kind"])}) for trigger in raw.get("triggers", ()))  # type: ignore[arg-type]
    return WorkflowDefinition(str(raw["workflow_id"]), int(raw["version"]), str(raw["name"]), steps, triggers, int(raw.get("max_runtime_seconds", 86_400)), raw.get("template"))


def _topological(steps: tuple[WorkflowStep, ...]) -> tuple[str, ...]:
    indegree = {step.id: len(step.depends_on) for step in steps}
    children = {step.id: [] for step in steps}
    for step in steps:
        for dep in step.depends_on:
            children[dep].append(step.id)
    ready = sorted(key for key, degree in indegree.items() if degree == 0)
    order: list[str] = []
    while ready:
        current = ready.pop(0)
        order.append(current)
        for child in sorted(children[current]):
            indegree[child] -= 1
            if indegree[child] == 0:
                ready.append(child)
        ready.sort()
    if len(order) != len(steps):
        raise ValueError("workflow dependency cycle detected")
    return tuple(order)


def _safe_json(value: object) -> object:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    if len(encoded.encode()) > _MAX_PAYLOAD_BYTES:
        raise ValueError("workflow payload exceeds 256 KiB")
    return json.loads(encoded)


def _jsonable(value: object) -> object:
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(v) for v in value]
    if isinstance(value, (WorkflowStepKind, WorkflowRunStatus, TriggerKind)):
        return value.value
    return value


def _bounded_text(value: str | None, name: str, maximum: int) -> str:
    if value is None or not isinstance(value, str) or len(value) > maximum:
        raise ValueError(f"{name} is invalid or too long")
    return value.strip()


def _name(value: str) -> str:
    value = _bounded_text(value, "name", 128)
    if not value:
        raise ValueError("name is required")
    return value


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ValueError("datetime must be timezone-aware")
    return value.astimezone(UTC)


def _parse(value: str) -> datetime:
    return datetime.fromisoformat(value).astimezone(UTC)
