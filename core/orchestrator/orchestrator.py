from collections.abc import Callable

from core.execution.command_runner import CommandRunner
from core.execution.execution_record import ExecutionRecord
from core.orchestrator.task_manager import TaskManager
from core.state.checkpoints import Checkpoint, CheckpointStore
from core.verification.evidence import Evidence, VerificationStatus
from core.verification.evidence_store import EvidenceStore


class Orchestrator:
    """Control-plane entry point with checkpoints, execution, and evidence."""

    def __init__(
        self,
        task_manager: TaskManager | None = None,
        checkpoint_store: CheckpointStore | None = None,
        evidence_store: EvidenceStore | None = None,
        command_runner: CommandRunner | None = None,
    ) -> None:
        self.tasks = task_manager or TaskManager()
        self.checkpoints = checkpoint_store or CheckpointStore()
        self.evidence = evidence_store or EvidenceStore()
        self.commands = command_runner

    def run(self, description: str, worker: Callable[[str], str]) -> str:
        task = self.tasks.create(description)
        task.start()
        try:
            result = worker(task.description)
        except Exception as exc:
            task.fail(str(exc))
            raise
        task.succeed(result)
        return result

    def checkpoint(self, task_id: str, description: str) -> Checkpoint:
        """Record a control-plane checkpoint for a known task."""
        self.tasks.get(task_id)
        return self.checkpoints.create(task_id, description)

    def execute(self, task_id: str, command: str, *, timeout: float = 60.0) -> ExecutionRecord:
        """Execute a command for a known task and record the execution evidence."""
        if self.commands is None:
            raise RuntimeError("Command runner is not configured")
        task = self.tasks.get(task_id)
        if task.status.value != "running":
            raise ValueError(f"Cannot execute command for task in state {task.status.value}")
        record = self.commands.run(task_id, command, timeout=timeout)
        status = VerificationStatus.VERIFIED if record.succeeded else VerificationStatus.FAILED
        details = record.stderr if not record.succeeded else record.stdout
        self.evidence.record(
            Evidence(
                claim=f"Command execution succeeded: {record.succeeded}",
                source=f"execution:{record.id}",
                verification_status=status,
                details=details,
            )
        )
        return record
