from __future__ import annotations

import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from core.state.task_state import Task, TaskStatus


class TaskManager:
    """Manage task lifecycle, dependencies, priorities, retries, and persistence."""

    def __init__(self, state_path: str | Path | None = None) -> None:
        self._tasks: dict[str, Task] = {}
        self._state_path = Path(state_path) if state_path is not None else None
        if self._state_path is not None and self._state_path.exists():
            self._load()

    def create(
        self,
        description: str,
        *,
        priority: int = 0,
        dependencies: tuple[str, ...] = (),
        max_attempts: int = 1,
    ) -> Task:
        if not description.strip():
            raise ValueError("Task description must not be empty")
        for dependency in dependencies:
            if dependency not in self._tasks:
                raise KeyError(f"Unknown task dependency: {dependency}")
        task = Task(
            description=description.strip(),
            priority=priority,
            dependencies=tuple(dependencies),
            max_attempts=max_attempts,
        )
        self._tasks[task.id] = task
        self._persist()
        return task

    def get(self, task_id: str) -> Task:
        try:
            return self._tasks[task_id]
        except KeyError as exc:
            raise KeyError(f"Unknown task: {task_id}") from exc

    def all(self) -> tuple[Task, ...]:
        return tuple(self._tasks.values())

    def ready(self) -> tuple[Task, ...]:
        """Return pending tasks whose dependencies have all succeeded, highest priority first."""
        ready_tasks = [
            task
            for task in self._tasks.values()
            if task.status is TaskStatus.PENDING
            and all(self.get(dep).status is TaskStatus.SUCCEEDED for dep in task.dependencies)
        ]
        return tuple(sorted(ready_tasks, key=lambda item: (-item.priority, item.created_at, item.id)))

    def retry(self, task_id: str) -> Task:
        task = self.get(task_id)
        if not task.retryable:
            raise ValueError(f"Task is not retryable: {task_id}")
        task.status = TaskStatus.PENDING
        task.error = None
        task.completed_at = None
        self._persist()
        return task

    def cancel(self, task_id: str, reason: str = "") -> Task:
        task = self.get(task_id)
        task.cancel(reason)
        self._persist()
        return task

    def persist(self) -> None:
        self._persist()

    def _persist(self) -> None:
        if self._state_path is None:
            return
        self._state_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"tasks": [self._serialize(task) for task in self._tasks.values()]}
        temporary = self._state_path.with_suffix(self._state_path.suffix + ".tmp")
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        temporary.replace(self._state_path)

    def _load(self) -> None:
        payload = json.loads(self._state_path.read_text(encoding="utf-8"))
        for item in payload.get("tasks", []):
            task = self._deserialize(item)
            self._tasks[task.id] = task

    @staticmethod
    def _serialize(task: Task) -> dict[str, object]:
        data = asdict(task)
        data["status"] = task.status.value
        data["created_at"] = task.created_at.isoformat()
        data["started_at"] = task.started_at.isoformat() if task.started_at else None
        data["completed_at"] = task.completed_at.isoformat() if task.completed_at else None
        return data

    @staticmethod
    def _deserialize(data: dict[str, object]) -> Task:
        def parse_datetime(value: object) -> datetime | None:
            return datetime.fromisoformat(value) if isinstance(value, str) else None

        return Task(
            description=str(data["description"]),
            id=str(data["id"]),
            status=TaskStatus(str(data["status"])),
            created_at=parse_datetime(data["created_at"]) or datetime.now(UTC),
            started_at=parse_datetime(data.get("started_at")),
            completed_at=parse_datetime(data.get("completed_at")),
            result=str(data["result"]) if data.get("result") is not None else None,
            error=str(data["error"]) if data.get("error") is not None else None,
            priority=int(data.get("priority", 0)),
            dependencies=tuple(str(item) for item in data.get("dependencies", [])),
            attempts=int(data.get("attempts", 0)),
            max_attempts=int(data.get("max_attempts", 1)),
        )
