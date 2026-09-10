from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4
import json


class CheckpointError(RuntimeError):
    """Raised when checkpoint state cannot be used safely."""


@dataclass(frozen=True)
class Checkpoint:
    task_id: str
    description: str
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    snapshot_id: str | None = None


class CheckpointStore:
    """Store immutable task checkpoints and optional workspace snapshot IDs."""

    def __init__(self, state_path: str | Path | None = None) -> None:
        self._checkpoints: dict[str, Checkpoint] = {}
        self._state_path = Path(state_path) if state_path is not None else None
        if self._state_path is not None and self._state_path.exists():
            self._load()

    def create(
        self,
        task_id: str,
        description: str,
        *,
        snapshot_id: str | None = None,
    ) -> Checkpoint:
        if not task_id.strip():
            raise ValueError("Task ID must not be empty")
        if not description.strip():
            raise ValueError("Checkpoint description must not be empty")
        if snapshot_id is not None and not snapshot_id.strip():
            raise ValueError("Snapshot ID must not be empty")
        checkpoint = Checkpoint(
            task_id=task_id.strip(),
            description=description.strip(),
            snapshot_id=snapshot_id.strip() if snapshot_id else None,
        )
        self._checkpoints[checkpoint.id] = checkpoint
        self._persist()
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

    def all(self) -> tuple[Checkpoint, ...]:
        return tuple(self._checkpoints.values())

    def _persist(self) -> None:
        if self._state_path is None:
            return
        self._state_path.parent.mkdir(parents=True, exist_ok=True)
        payload = [
            {
                "task_id": checkpoint.task_id,
                "description": checkpoint.description,
                "id": checkpoint.id,
                "created_at": checkpoint.created_at.isoformat(),
                "snapshot_id": checkpoint.snapshot_id,
            }
            for checkpoint in self._checkpoints.values()
        ]
        temporary = self._state_path.with_suffix(self._state_path.suffix + ".tmp")
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        temporary.replace(self._state_path)

    def _load(self) -> None:
        payload = json.loads(self._state_path.read_text(encoding="utf-8"))
        for item in payload:
            checkpoint = Checkpoint(
                task_id=str(item["task_id"]),
                description=str(item["description"]),
                id=str(item["id"]),
                created_at=datetime.fromisoformat(str(item["created_at"])),
                snapshot_id=str(item["snapshot_id"]) if item.get("snapshot_id") else None,
            )
            self._checkpoints[checkpoint.id] = checkpoint
