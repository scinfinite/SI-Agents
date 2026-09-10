from collections.abc import Callable
from pathlib import Path

from core.execution.command_runner import CommandRunner
from core.execution.execution_record import ExecutionRecord
from core.orchestrator.task_manager import TaskManager
from core.state.checkpoints import Checkpoint, CheckpointStore
from core.state.filesystem_snapshot import FilesystemSnapshotStore
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
        snapshot_store: FilesystemSnapshotStore | None = None,
    ) -> None:
        self.tasks = task_manager or TaskManager()
        self.checkpoints = checkpoint_store or CheckpointStore()
        self.evidence = evidence_store or EvidenceStore()
        self.commands = command_runner
        self.snapshots = snapshot_store

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

    def checkpoint(
        self,
        task_id: str,
        description: str,
        *,
        workspace: str | Path | None = None,
    ) -> Checkpoint:
        """Record a checkpoint, optionally backed by a filesystem snapshot."""
        self.tasks.get(task_id)
        snapshot_id = None
        if workspace is not None:
            if self.snapshots is None:
                raise RuntimeError("Snapshot store is not configured")
            snapshot_id = self.snapshots.create(workspace).id
        return self.checkpoints.create(task_id, description, snapshot_id=snapshot_id)

    def restore_checkpoint(self, checkpoint_id: str, *, approval_granted: bool = False) -> None:
        """Restore a snapshot-backed checkpoint with explicit destructive approval."""
        checkpoint = self.checkpoints.get(checkpoint_id)
        if checkpoint.snapshot_id is None:
            raise RuntimeError("Checkpoint has no workspace snapshot")
        if self.snapshots is None:
            raise RuntimeError("Snapshot store is not configured")
        self.snapshots.restore(checkpoint.snapshot_id, approval_granted=approval_granted)

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
