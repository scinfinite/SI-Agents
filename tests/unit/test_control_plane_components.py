import pytest

from core.orchestrator.agent_coordinator import AgentCoordinator
from core.orchestrator.context_manager import ContextManager
from core.orchestrator.task_manager import TaskManager
from core.orchestrator.workflow_engine import WorkflowEngine
from core.policies.approval_engine import ApprovalEngine, ApprovalStatus
from core.policies.permission_engine import PermissionDecision, PermissionEngine, PermissionScope


def test_contexts_are_isolated() -> None:
    manager = ContextManager()
    first = manager.create("task-1")
    second = manager.create("task-2")
    first.set("value", 1)
    assert first.require("value") == 1
    assert second.get("value") is None
    with pytest.raises(ValueError):
        manager.create("task-1")


def test_agent_coordinator_registers_and_delegates() -> None:
    coordinator = AgentCoordinator()
    coordinator.register("developer", lambda description, context: f"{description}:{context.task_id}")
    context = ContextManager().create("task-1")
    assert coordinator.delegate("developer", "repair", context) == "repair:task-1"
    with pytest.raises(KeyError):
        coordinator.get("missing")


def test_workflow_engine_executes_dependency_chain() -> None:
    manager = TaskManager()
    first = manager.create("first")
    second = manager.create("second", dependencies=(first.id,))
    engine = WorkflowEngine(manager)
    completed = engine.run({
        first.id: lambda task: "one",
        second.id: lambda task: "two",
    })
    assert [task.id for task in completed] == [first.id, second.id]
    assert second.result == "two"


def test_workflow_engine_detects_cycles() -> None:
    manager = TaskManager()
    first = manager.create("first")
    second = manager.create("second", dependencies=(first.id,))
    first.dependencies = (second.id,)
    with pytest.raises(ValueError, match="cycle"):
        WorkflowEngine(manager).validate()


def test_approval_lifecycle_is_explicit() -> None:
    engine = ApprovalEngine()
    request = engine.request("task-1", "publication", "release artifact")
    assert request.status is ApprovalStatus.PENDING
    engine.approve(request.id)
    assert request.status is ApprovalStatus.APPROVED
    assert request.decided_at is not None
    with pytest.raises(ValueError):
        engine.reject(request.id)


def test_permission_scope_restricts_matching_agent_and_tool() -> None:
    engine = PermissionEngine(
        scopes=(PermissionScope(agent="developer", tool="shell", capabilities=frozenset({"local_command"})),)
    )
    assert engine.decide("local_command", agent="developer", tool="shell") is PermissionDecision.ALLOW
    assert engine.decide("local_command", agent="developer", tool="git") is PermissionDecision.DENY
    assert engine.decide("local_command", agent="tester", tool="shell") is PermissionDecision.DENY
