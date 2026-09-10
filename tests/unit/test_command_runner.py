from core.execution.command_runner import CommandRunner
from core.orchestrator.orchestrator import Orchestrator
from core.policies.permission_engine import PermissionEngine
from tools.sandbox.local_sandbox import LocalSandbox


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


def test_command_runner_honors_permission_denial(tmp_path) -> None:
    runner = CommandRunner(
        LocalSandbox(tmp_path),
        permissions=PermissionEngine(allow_local_commands=False),
    )
    orchestrator = Orchestrator(command_runner=runner)
    task = orchestrator.tasks.create("blocked command")
    task.start()

    try:
        orchestrator.execute(task.id, "python -c \"print('no')\"")
    except PermissionError:
        pass
    else:
        raise AssertionError("Denied command was executed")
