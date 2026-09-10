from core.execution.command_runner import CommandRunner
from core.orchestrator.orchestrator import Orchestrator
from tools.sandbox.local_sandbox import LocalSandbox
from core.verification.evidence import VerificationStatus


def test_failed_execution_is_recorded_as_failed_evidence(tmp_path) -> None:
    orchestrator = Orchestrator(command_runner=CommandRunner(LocalSandbox(tmp_path)))
    task = orchestrator.tasks.create("run failing verification")
    task.start()

    record = orchestrator.execute(
        task.id,
        "python -c \"import sys; print('failure', file=sys.stderr); sys.exit(2)\"",
    )

    assert not record.succeeded
    evidence = orchestrator.evidence.all()
    assert len(evidence) == 1
    assert evidence[0].verification_status is VerificationStatus.FAILED
    assert "failure" in evidence[0].details
