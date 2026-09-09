from core.state.task_state import Task


class TaskManager:
    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}

    def create(self, description: str) -> Task:
        if not description.strip():
            raise ValueError("Task description must not be empty")
        task = Task(description=description.strip())
        self._tasks[task.id] = task
        return task

    def get(self, task_id: str) -> Task:
        try:
            return self._tasks[task_id]
        except KeyError as exc:
            raise KeyError(f"Unknown task: {task_id}") from exc

    def all(self) -> tuple[Task, ...]:
        return tuple(self._tasks.values())
