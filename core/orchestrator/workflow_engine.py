from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from core.orchestrator.task_manager import TaskManager
from core.state.task_state import Task, TaskStatus


@dataclass(frozen=True)
class WorkflowStep:
    task_id: str
    worker: Callable[[Task], str]


class WorkflowEngine:
    """Execute ready tasks in dependency order while preserving task state."""

    def __init__(self, task_manager: TaskManager) -> None:
        self.tasks = task_manager

    def validate(self) -> None:
        for task in self.tasks.all():
            self._visit(task.id, visiting=set(), visited=set())

    def run(self, workers: dict[str, Callable[[Task], str]]) -> tuple[Task, ...]:
        self.validate()
        completed: list[Task] = []
        while True:
            ready = self.tasks.ready()
            if not ready:
                break
            progressed = False
            for task in ready:
                worker = workers.get(task.id)
                if worker is None:
                    continue
                task.start()
                try:
                    task.succeed(worker(task))
                except Exception as exc:  # noqa: BLE001 - worker failures belong to task state.
                    task.fail(str(exc))
                self.tasks.persist()
                completed.append(task)
                progressed = True
            if not progressed:
                break
        return tuple(completed)

    def blocked(self) -> tuple[Task, ...]:
        """Return pending tasks blocked by a failed or cancelled dependency."""
        return tuple(
            task
            for task in self.tasks.all()
            if task.status is TaskStatus.PENDING
            and any(
                self.tasks.get(dep).status in {TaskStatus.FAILED, TaskStatus.CANCELLED}
                for dep in task.dependencies
            )
        )

    def _visit(self, task_id: str, *, visiting: set[str], visited: set[str]) -> None:
        if task_id in visiting:
            raise ValueError(f"Task dependency cycle detected at: {task_id}")
        if task_id in visited:
            return
        visiting.add(task_id)
        task = self.tasks.get(task_id)
        for dependency in task.dependencies:
            self._visit(dependency, visiting=visiting, visited=visited)
        visiting.remove(task_id)
        visited.add(task_id)
