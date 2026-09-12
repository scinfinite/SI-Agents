from datetime import UTC, datetime, timedelta
from threading import Barrier, Thread

import pytest

from core.automation.workflows import (
    TriggerKind,
    WorkflowDefinition,
    WorkflowEngine,
    WorkflowRunStatus,
    WorkflowStep,
    WorkflowStepKind,
    WorkflowTrigger,
)

NOW = datetime(2026, 9, 12, 10, 0, tzinfo=UTC)


def definition(*steps: WorkflowStep, triggers=()):
    return WorkflowDefinition("wf", 1, "Workflow", tuple(steps), tuple(triggers))


def test_dag_order_and_condition_branch() -> None:
    calls: list[str] = []
    engine = WorkflowEngine()
    engine.register_action("a", lambda value: calls.append("a") or {"ok": True})
    engine.register_action("b", lambda value: calls.append("b") or {"ok": True})
    engine.register_condition("yes", lambda variables: variables["allow"] is True)
    engine.register(definition(
        WorkflowStep("a", WorkflowStepKind.TASK, action="a"),
        WorkflowStep("gate", WorkflowStepKind.CONDITION, condition="yes", depends_on=("a",)),
        WorkflowStep("b", WorkflowStepKind.TASK, action="b", depends_on=("gate",)),
    ))
    run = engine.start("wf", variables={"allow": True})
    assert engine.tick(run.run_id).status is WorkflowRunStatus.SUCCEEDED
    assert calls == ["a", "b"]


def test_false_condition_skips_branch() -> None:
    calls: list[str] = []
    engine = WorkflowEngine()
    engine.register_action("work", lambda value: calls.append("work"))
    engine.register_condition("enabled", lambda variables: False)
    engine.register(definition(
        WorkflowStep("gate", WorkflowStepKind.CONDITION, condition="enabled"),
        WorkflowStep("work", WorkflowStepKind.TASK, action="work", depends_on=("gate",)),
    ))
    run = engine.start("wf")
    assert engine.tick(run.run_id).status is WorkflowRunStatus.SUCCEEDED
    assert run.step_states == {"gate": "skipped", "work": "skipped"}
    assert calls == []


def test_wait_is_durable_and_resume_continues(tmp_path) -> None:
    path = tmp_path / "workflow.json"
    engine = WorkflowEngine(state_path=path)
    engine.register_action("done", lambda value: {"done": True})
    engine.register(definition(
        WorkflowStep("wait", WorkflowStepKind.WAIT, wait_seconds=30),
        WorkflowStep("done", WorkflowStepKind.TASK, action="done", depends_on=("wait",)),
    ))
    run = engine.start("wf")
    run.created_at = NOW.isoformat()
    waiting = engine.tick(run.run_id, now=NOW)
    assert waiting.status is WorkflowRunStatus.WAITING
    restored = WorkflowEngine(state_path=path)
    restored.register_action("done", lambda value: {"done": True})
    resumed = restored.tick(run.run_id, now=NOW + timedelta(seconds=31))
    assert resumed.status is WorkflowRunStatus.SUCCEEDED
    assert resumed.step_states["wait"] == "succeeded"


def test_human_gate_requires_explicit_approval() -> None:
    engine = WorkflowEngine()
    engine.register_action("done", lambda value: None)
    engine.register(definition(
        WorkflowStep("gate", WorkflowStepKind.HUMAN, approval_key="approved"),
        WorkflowStep("done", WorkflowStepKind.TASK, action="done", depends_on=("gate",)),
    ))
    run = engine.start("wf")
    run.created_at = NOW.isoformat()
    assert engine.tick(run.run_id, now=NOW).status is WorkflowRunStatus.WAITING
    assert run.step_states["gate"] == "waiting"
    assert engine.resume(run.run_id, variables={"approved": True}, now=NOW).status is WorkflowRunStatus.SUCCEEDED


def test_fanout_and_loop_are_bounded() -> None:
    values: list[int] = []
    engine = WorkflowEngine()
    engine.register_action("fan", lambda item: values.append(item) or item * 2)
    engine.register_action("inc", lambda variables: variables.__setitem__("n", variables["n"] + 1) or variables["n"])
    engine.register_condition("done", lambda variables: variables["n"] >= 3)
    engine.register(definition(
        WorkflowStep("fan", WorkflowStepKind.FANOUT, action="fan", items_key="items"),
        WorkflowStep("loop", WorkflowStepKind.LOOP, action="inc", condition="done", max_iterations=4, depends_on=("fan",)),
    ))
    run = engine.start("wf", variables={"items": [1, 2, 3], "n": 0})
    assert engine.tick(run.run_id).status is WorkflowRunStatus.SUCCEEDED
    assert values == [1, 2, 3]
    assert run.variables["n"] == 3


def test_event_webhook_and_idempotency() -> None:
    engine = WorkflowEngine()
    engine.register(definition(
        WorkflowStep("event", WorkflowStepKind.TASK, action="event"),
        triggers=(WorkflowTrigger(TriggerKind.EVENT, "deploy"), WorkflowTrigger(TriggerKind.WEBHOOK, "hook")),
    ))
    engine.register_action("event", lambda value: value)
    first = engine.start("wf", idempotency_key="same")
    assert engine.start("wf", idempotency_key="same").run_id == first.run_id
    with pytest.raises(ValueError):
        engine.start("wf", idempotency_key="same", subject="different")
    assert len(engine.event("deploy", {"id": "42"}, subject="user")) == 1
    hooks = engine.webhook("hook", {"id": "43"}, subject="system")
    assert len(hooks) == 1 and hooks[0].trigger == "hook"


def test_interval_trigger_is_time_based() -> None:
    engine = WorkflowEngine()
    engine.register_action("work", lambda value: None)
    engine.register(definition(
        WorkflowStep("work", WorkflowStepKind.TASK, action="work"),
        triggers=(WorkflowTrigger(TriggerKind.INTERVAL, "every-minute", interval_seconds=60),),
    ))
    assert len(engine.due_intervals(now=NOW)) == 1
    run = engine.trigger_intervals(now=NOW)[0]
    run.created_at = NOW.isoformat()
    assert run.trigger == "interval"
    assert engine.due_intervals(now=NOW + timedelta(seconds=59)) == ()
    assert len(engine.due_intervals(now=NOW + timedelta(seconds=61))) == 1


def test_retry_and_runtime_timeout() -> None:
    attempts = {"count": 0}
    engine = WorkflowEngine()

    def flaky(value):
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise RuntimeError("temporary")
        return "ok"

    engine.register_action("flaky", flaky)
    engine.register(definition(WorkflowStep("work", WorkflowStepKind.TASK, action="flaky", retry_attempts=3)))
    run = engine.start("wf")
    assert engine.tick(run.run_id).status is WorkflowRunStatus.SUCCEEDED
    assert attempts["count"] == 3

    timeout = WorkflowDefinition("timeout", 1, "Timeout", (WorkflowStep("w", WorkflowStepKind.WAIT, wait_seconds=1),), max_runtime_seconds=1)
    engine.register(timeout)
    timed = engine.start("timeout")
    timed.created_at = (NOW - timedelta(seconds=2)).isoformat()
    assert engine.tick(timed.run_id, now=NOW).status is WorkflowRunStatus.FAILED


def test_concurrent_idempotency_is_atomic() -> None:
    engine = WorkflowEngine()
    engine.register_action("work", lambda value: None)
    engine.register(definition(WorkflowStep("work", WorkflowStepKind.TASK, action="work")))
    barrier = Barrier(8)
    results = []

    def start() -> None:
        barrier.wait()
        results.append(engine.start("wf", idempotency_key="atomic"))

    threads = [Thread(target=start) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert {run.run_id for run in results} == {results[0].run_id}


def test_cancel_and_invalid_persistence_fail_closed(tmp_path) -> None:
    path = tmp_path / "bad.json"
    path.write_text("not-json", encoding="utf-8")
    with pytest.raises(ValueError):
        WorkflowEngine(state_path=path)

    engine = WorkflowEngine()
    engine.register_action("work", lambda value: None)
    engine.register(definition(WorkflowStep("work", WorkflowStepKind.TASK, action="work")))
    run = engine.start("wf")
    cancelled = engine.cancel(run.run_id, "operator stop")
    assert cancelled.status is WorkflowRunStatus.CANCELLED
    with pytest.raises(ValueError):
        engine.resume(run.run_id)


def test_versioning_templates_and_cycle_rejection() -> None:
    engine = WorkflowEngine()
    base = definition(WorkflowStep("a", WorkflowStepKind.TASK, action="a"))
    engine.register_action("a", lambda value: None)
    engine.register_template("release", base)
    created = engine.instantiate("release", "release-v1", 1)
    assert created.template == "release"
    with pytest.raises(ValueError):
        WorkflowDefinition("cycle", 1, "Cycle", (
            WorkflowStep("a", WorkflowStepKind.TASK, action="a", depends_on=("b",)),
            WorkflowStep("b", WorkflowStepKind.TASK, action="a", depends_on=("a",)),
        ))


def test_payload_and_fanout_limits_fail_closed() -> None:
    engine = WorkflowEngine()
    engine.register_action("fan", lambda item: item)
    engine.register(definition(WorkflowStep("fan", WorkflowStepKind.FANOUT, action="fan", items_key="items")))
    run = engine.start("wf", variables={"items": list(range(257))})
    assert engine.tick(run.run_id).status is WorkflowRunStatus.FAILED
    with pytest.raises(ValueError):
        engine.start("wf", variables={"blob": "x" * (256 * 1024 + 1)})


def test_failure_runs_compensation_in_reverse_order() -> None:
    calls: list[str] = []
    engine = WorkflowEngine()
    engine.register_action("ok", lambda value: calls.append("ok"))
    engine.register_action("fail", lambda value: (_ for _ in ()).throw(RuntimeError("boom")))
    engine.register_action("undo", lambda value: calls.append("undo"))
    engine.register(definition(
        WorkflowStep("one", WorkflowStepKind.TASK, action="ok", compensation_action="undo"),
        WorkflowStep("two", WorkflowStepKind.TASK, action="fail", depends_on=("one",)),
    ))
    run = engine.start("wf")
    assert engine.tick(run.run_id).status is WorkflowRunStatus.FAILED
    assert calls == ["ok", "undo"]
