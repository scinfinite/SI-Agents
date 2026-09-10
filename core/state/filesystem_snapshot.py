from __future__ import annotations

import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from core.policies.permission_engine import PermissionEngine


class SnapshotError(RuntimeError):
    """Raised when a workspace snapshot cannot be created or restored safely."""


@dataclass(frozen=True)
class FilesystemSnapshot:
    id: str
    workspace: Path
    snapshot_path: Path


class FilesystemSnapshotStore:
    """Create and restore complete workspace snapshots outside the workspace."""

    def __init__(self, *, permissions: PermissionEngine | None = None) -> None:
        self.permissions = permissions or PermissionEngine()
        self._snapshots: dict[str, FilesystemSnapshot] = {}

    def create(self, workspace: str | Path) -> FilesystemSnapshot:
        root = self._workspace(workspace)
        self._reject_symlink_entries(root)
        snapshot_path = Path(tempfile.mkdtemp(prefix="si-agents-checkpoint-")) / "workspace"
        shutil.copytree(root, snapshot_path, symlinks=True)
        snapshot = FilesystemSnapshot(uuid4().hex, root, snapshot_path)
        self._snapshots[snapshot.id] = snapshot
        return snapshot

    def get(self, snapshot_id: str) -> FilesystemSnapshot:
        try:
            return self._snapshots[snapshot_id]
        except KeyError as exc:
            raise SnapshotError(f"Unknown snapshot: {snapshot_id}") from exc

    def restore(self, snapshot_id: str, *, approval_granted: bool = False) -> None:
        self.permissions.require("destructive_filesystem", approval_granted=approval_granted)
        snapshot = self.get(snapshot_id)
        root = self._workspace(snapshot.workspace)
        if not snapshot.snapshot_path.is_dir():
            raise SnapshotError(f"Snapshot data is missing: {snapshot.snapshot_path}")
        self._reject_symlink_entries(root)
        for child in root.iterdir():
            if child.is_dir() and not child.is_symlink():
                shutil.rmtree(child)
            else:
                child.unlink()
        for child in snapshot.snapshot_path.iterdir():
            target = root / child.name
            if child.is_dir() and not child.is_symlink():
                shutil.copytree(child, target, symlinks=True)
            else:
                shutil.copy2(child, target, follow_symlinks=False)

    def discard(self, snapshot_id: str) -> None:
        """Delete snapshot data that is no longer needed."""
        snapshot = self.get(snapshot_id)
        shutil.rmtree(snapshot.snapshot_path.parent)
        del self._snapshots[snapshot.id]

    @staticmethod
    def _workspace(workspace: str | Path) -> Path:
        root = Path(workspace).resolve()
        if not root.is_dir():
            raise SnapshotError(f"Workspace does not exist: {root}")
        if Path(workspace).is_symlink():
            raise SnapshotError("Workspace root must not be a symlink")
        return root

    @staticmethod
    def _reject_symlink_entries(root: Path) -> None:
        for path in root.rglob("*"):
            if path.is_symlink():
                raise SnapshotError(f"Workspace contains unsupported symlink: {path}")
