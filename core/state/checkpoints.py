from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4


class CheckpointError(RuntimeError):
    """Raised when checkpoint state cannot be used safely."""


@dataclass(frozen=True)
class Checkpoint:
    task_id: str
    description: str
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class CheckpointStore:
    """Store immutable task checkpoints for control-plane state.

    This records a checkpoint marker; it does not snapshot or restore files. A
    filesystem or Git-backed rollback mechanism must be implemented separately
    before SI-Agents treats a checkpoint as protection against workspace changes.
    """

    def __init__(self) -> None:
        self._checkpoints: dict[str, Checkpoint] = {}

    def create(self, task_id: str, description: str) -> Checkpoint:
        if not task_id.strip():
            raise ValueError("Task ID must not be empty")
        if not description.strip():
            raise ValueError("Checkpoint description must not be empty")
        checkpoint = Checkpoint(task_id=task_id.strip(), description=description.strip())
        self._checkpoints[checkpoint.id] = checkpoint
        return checkpoint

    def get(self, checkpoint_id: str) -> Checkpoint:
        try:
            return self._checkpoints[checkpoint_id]
        except KeyError as exc:
            raise CheckpointError(f"Unknown checkpoint: {checkpoint_id}") from exc

    def for_task(self, task_id: str) -> tuple[Checkpoint, ...]:
        if not task_id.strip():
            raise ValueError("Task ID must not be empty")
        return tuple(
            checkpoint
            for checkpoint in self._checkpoints.values()
            if checkpoint.task_id == task_id.strip()
        )
