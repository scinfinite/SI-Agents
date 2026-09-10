from __future__ import annotations

import pytest

from agents.base import AgentSpec
from agents.debugger import DebuggerAgent
from agents.developer import DeveloperAgent
from agents.tester import TesterAgent
from core.orchestrator.brain_models import Problem
from core.orchestrator.engineering_workflow import EngineeringWorkflow
from core.orchestrator.orchestrator import Orchestrator
from core.policies.permission_engine import PermissionDenied, PermissionEngine
from core.state.task_state import TaskStatus


def test_agent_specs_declare_boundaries_and_success_contracts() -> None:
    for agent in (DebuggerAgent(), DeveloperAgent(), TesterAgent()):
        assert isinstance(agent.spec, AgentSpec)
        assert agent.spec.deliverables
        assert agent.spec.success_criteria
        assert agent.spec.boundaries


def test_engineering_workflow_uses_brain_and_records_handoffs() -> None:
    events: list[str] = []
    workflow = EngineeringWorkflow(Orchestrator())
    problem = Problem(
        description="Fix broken addition",
        acceptance_criteria=("add returns the arithmetic sum",),
    )
    result = workflow.run(
        "repair addition",
        inspect=lambda: "app.py returns subtraction",
        reproduce=lambda: events.append("reproduce") is None or True,
        diagnose=lambda: "return operator is subtraction instead of addition",
        repair=lambda cause: events.append(f"repair:{cause}") or "changed '-' to '+'",
        verify=lambda: events.append("verify") is None or True,
        red_team=lambda: events.append("red_team") is None or True,
        regression=lambda: events.append("regression") is None or True,
        problem=problem,
    )
    assert result.plan_id
    assert result.debugger.handoff["root_cause"].startswith("return operator")
    assert result.developer.handoff["repair"] == "changed '-' to '+'"
    assert result.tester.handoff["verified"] is True
    assert events == ["reproduce", "repair:return operator is subtraction instead of addition", "verify", "red_team", "regression"]
    task = workflow.orchestrator.tasks.get(result.task_id)
    assert task.status is TaskStatus.SUCCEEDED
    assert len(workflow.orchestrator.evidence.all()) >= 5


def test_developer_never_runs_when_workspace_write_is_denied() -> None:
    called = False
    permissions = PermissionEngine(allow_write_workspace=False)
    workflow = EngineeringWorkflow(Orchestrator(permission_engine=permissions))
    with pytest.raises(PermissionDenied):
        workflow.run(
            "denied repair",
            inspect=lambda: "failure found",
            reproduce=lambda: True,
            diagnose=lambda: "bad operator",
            repair=lambda cause: (_ for _ in ()).throw(AssertionError("repair must not run")),
            verify=lambda: True,
            red_team=lambda: True,
            regression=lambda: True,
        )
    assert called is False
    assert workflow.orchestrator.tasks.all()[0].status is TaskStatus.FAILED


def test_debugger_does_not_claim_success_without_reproduction() -> None:
    agent = DebuggerAgent()
    with pytest.raises(RuntimeError, match="could not reproduce"):
        agent.run(
            context=__import__("agents.base", fromlist=["AgentContext"]).AgentContext("task"),
            reproduce=lambda: False,
            diagnose=lambda: "should never be accepted",
            permissions=PermissionEngine(),
        )
