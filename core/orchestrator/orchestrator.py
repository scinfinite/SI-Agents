from collections.abc import Callable

from core.orchestrator.task_manager import TaskManager


class Orchestrator:
    """Minimal control-plane entry point.

    Execution is deliberately dependency-injected so real tools and agents can be
    added without coupling task state to a specific model or runtime.
    """

    def __init__(self, task_manager: TaskManager | None = None) -> None:
        self.tasks = task_manager or TaskManager()

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
