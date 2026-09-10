from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class TaskContext:
    """Bounded, task-local context shared by orchestrated components."""

    task_id: str
    values: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def set(self, key: str, value: Any) -> None:
        if not key.strip():
            raise ValueError("Context key must not be empty")
        self.values[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.values.get(key, default)

    def require(self, key: str) -> Any:
        if key not in self.values:
            raise KeyError(f"Missing context value: {key}")
        return self.values[key]


class ContextManager:
    """Maintain isolated contexts keyed by task ID."""

    def __init__(self) -> None:
        self._contexts: dict[str, TaskContext] = {}

    def create(self, task_id: str) -> TaskContext:
        if not task_id.strip():
            raise ValueError("Task ID must not be empty")
        if task_id in self._contexts:
            raise ValueError(f"Context already exists for task: {task_id}")
        context = TaskContext(task_id=task_id)
        self._contexts[task_id] = context
        return context

    def get(self, task_id: str) -> TaskContext:
        try:
            return self._contexts[task_id]
        except KeyError as exc:
            raise KeyError(f"Unknown task context: {task_id}") from exc

    def get_or_create(self, task_id: str) -> TaskContext:
        return self._contexts.get(task_id) or self.create(task_id)

    def remove(self, task_id: str) -> None:
        self._contexts.pop(task_id, None)
