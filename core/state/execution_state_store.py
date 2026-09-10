from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from core.state.execution_state import ExecutionState, ExecutionStatus


class ExecutionStateStore:
    """Durable JSON store for execution lifecycle records."""

    def __init__(self, state_path: str | Path | None = None) -> None:
        self._state_path = Path(state_path) if state_path is not None else None
        self._states: dict[str, ExecutionState] = {}
        if self._state_path is not None and self._state_path.exists():
            self._load()

    def record(self, state: ExecutionState) -> ExecutionState:
        if state.id in self._states:
            raise ValueError(f"Execution state already exists: {state.id}")
        self._states[state.id] = state
        self._persist()
        return state

    def update(self, state: ExecutionState) -> None:
        if state.id not in self._states:
            raise KeyError(f"Unknown execution state: {state.id}")
        self._states[state.id] = state
        self._persist()

    def get(self, execution_id: str) -> ExecutionState:
        try:
            return self._states[execution_id]
        except KeyError as exc:
            raise KeyError(f"Unknown execution state: {execution_id}") from exc

    def for_task(self, task_id: str) -> tuple[ExecutionState, ...]:
        return tuple(state for state in self._states.values() if state.task_id == task_id)

    def all(self) -> tuple[ExecutionState, ...]:
        return tuple(self._states.values())

    def _persist(self) -> None:
        if self._state_path is None:
            return
        self._state_path.parent.mkdir(parents=True, exist_ok=True)
        payload = [self._serialize(state) for state in self._states.values()]
        temporary = self._state_path.with_suffix(self._state_path.suffix + ".tmp")
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        temporary.replace(self._state_path)

    def _load(self) -> None:
        payload = json.loads(self._state_path.read_text(encoding="utf-8"))
        for item in payload:
            state = ExecutionState(
                task_id=str(item["task_id"]),
                status=ExecutionStatus(str(item["status"])),
                id=str(item["id"]),
                created_at=datetime.fromisoformat(str(item["created_at"])),
                started_at=self._parse(item.get("started_at")),
                completed_at=self._parse(item.get("completed_at")),
                attempt=int(item.get("attempt", 0)),
                error=str(item["error"]) if item.get("error") is not None else None,
            )
            self._states[state.id] = state

    @staticmethod
    def _parse(value: object) -> datetime | None:
        return datetime.fromisoformat(value) if isinstance(value, str) else None

    @staticmethod
    def _serialize(state: ExecutionState) -> dict[str, object]:
        return {
            "task_id": state.task_id,
            "status": state.status.value,
            "id": state.id,
            "created_at": state.created_at.astimezone(UTC).isoformat(),
            "started_at": state.started_at.astimezone(UTC).isoformat() if state.started_at else None,
            "completed_at": state.completed_at.astimezone(UTC).isoformat() if state.completed_at else None,
            "attempt": state.attempt,
            "error": state.error,
        }
