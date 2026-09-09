from collections.abc import Callable

from core.orchestrator.task_manager import TaskManager
from core.state.checkpoints import Checkpoint, CheckpointStore


class Orchestrator:
    """Minimal control-plane entry point with checkpoint support."""

    def __init__(
        self,
        task_manager: TaskManager | None = None,
        checkpoint_store: CheckpointStore | None = None,
    ) -> None:
        self.tasks = task_manager or TaskManager()
        self.checkpoints = checkpoint_store or CheckpointStore()

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
