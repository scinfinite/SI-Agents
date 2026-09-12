from datetime import UTC, datetime, timedelta

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


def test_dag_parallel_order_and_condition_branch() -> None:
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


def test_false_condition_skips_conditional_step() -> None:
    calls: list[str] = []
    engine = WorkflowEngine()
    engine.register_action("work", lambda value: calls.append("work"))
    engine.register_condition("enabled", lambda variables: False)
    engine.register(definition(
        WorkflowStep("work", WorkflowStepKind.TASK, action="work", condition="enabled"),
    ))
    run = engine.start("wf")
    assert engine.tick(run.run_id).status is WorkflowRunStatus.SUCCEEDED
    assert run.step_states["work"] == "skipped"
    assert calls == []


def test_wait_is_durable_and_resume_continues(tmp_path: object) -> None:
    path = tmp_path / "workflow.json"
    engine = WorkflowEngine(state_path=path)
    engine.register_action("done", lambda value: {"done": True})
    engine.register(definition(
        WorkflowStep("wait", WorkflowStepKind.WAIT, wait_seconds=30),
        WorkflowStep("done", WorkflowStepKind.TASK, action="done", depends_on=("wait",)),
    ))
    run = engine.start("wf")
    waiting = engine.tick(run.run_id, now=NOW)
    assert waiting.status is WorkflowRunStatus.WAITING
    assert waiting.step_states["wait"] == "waiting"
    restored = WorkflowEngine(state_path=path)
    restored.register_action("done", lambda value: {"done": True})
    resumed = restored.tick(run.run_id, now=NOW + timedelta(seconds=31))
    assert resumed.status is WorkflowRunStatus.SUCCEEDED


def test_human_gate_requires_explicit_approval() -> None:
    engine = WorkflowEngine()
    engine.register_action("done", lambda value: None)
    engine.register(definition(
        WorkflowStep("gate", WorkflowStepKind.HUMAN, approval_key="approved"),
        WorkflowStep("done", WorkflowStepKind.TASK, action="done", depends_on=("gate",)),
    ))
    run = engine.start("wf")
    assert engine.tick(run.run_id, now=NOW).status is WorkflowRunStatus.WAITING
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


def test_event_trigger_and_idempotency() -> None:
    engine = WorkflowEngine()
    engine.register(definition(
        WorkflowStep("event", WorkflowStepKind.TASK, action="event"),
        triggers=(WorkflowTrigger(TriggerKind.EVENT, "deploy"),),
    ))
    engine.register_action("event", lambda value: value)
    first = engine.start("wf", idempotency_key="same")
    assert engine.start("wf", idempotency_key="same").run_id == first.run_id
    runs = engine.event("deploy", {"id": "42"}, subject="user")
    assert len(runs) == 1
    assert runs[0].trigger == "deploy"


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
