import pytest

from core.execution.command_runner import CommandRunner
from core.orchestrator.orchestrator import Orchestrator
from core.policies.permission_engine import PermissionEngine
from tools.sandbox.command_policy import CommandPolicyError
from tools.sandbox.local_sandbox import LocalSandbox
from tools.sandbox.sandbox_result import CommandResult


class StubBackend:
    def __init__(self, workspace: str) -> None:
        self.workspace = workspace
        self.commands: list[str] = []

    def run(self, command: str, *, timeout: float = 60.0) -> CommandResult:
        self.commands.append(command)
        return CommandResult(command, 0, "stubbed", "")


def test_command_execution_is_correlated_to_task_and_evidence(tmp_path) -> None:
    runner = CommandRunner(LocalSandbox(tmp_path))
    orchestrator = Orchestrator(command_runner=runner)
    task = orchestrator.tasks.create("run verification")
    task.start()

    record = orchestrator.execute(task.id, "python -c \"print('verified')\"")

    assert record.task_id == task.id
    assert record.succeeded
    evidence = orchestrator.evidence.all()
    assert len(evidence) == 1
    assert evidence[0].source == f"execution:{record.id}"


def test_command_runner_accepts_backend_without_local_sandbox() -> None:
    backend = StubBackend("/isolated/workspace")
    runner = CommandRunner(backend)

    record = runner.run("task-1", "verify", timeout=5)

    assert backend.commands == ["verify"]
    assert record.task_id == "task-1"
    assert record.workspace == "/isolated/workspace"
    assert record.stdout == "stubbed"
    assert record.succeeded


def test_command_runner_honors_permission_denial(tmp_path) -> None:
    runner = CommandRunner(
        LocalSandbox(tmp_path),
        permissions=PermissionEngine(allow_local_commands=False),
    )
    orchestrator = Orchestrator(command_runner=runner)
    task = orchestrator.tasks.create("blocked command")
    task.start()

    with pytest.raises(PermissionError):
        orchestrator.execute(task.id, "python -c \"print('no')\"")


def test_command_policy_blocks_destructive_command_before_backend() -> None:
    backend = StubBackend("/workspace")
    runner = CommandRunner(backend)

    with pytest.raises(CommandPolicyError):
        runner.run("task-1", "rm -rf /")

    assert backend.commands == []
