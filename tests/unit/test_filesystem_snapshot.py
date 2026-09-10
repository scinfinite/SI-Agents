from pathlib import Path

import pytest

from core.policies.permission_engine import PermissionEngine
from core.state.filesystem_snapshot import FilesystemSnapshotStore, SnapshotError


def test_filesystem_snapshot_restores_workspace_with_approval(tmp_path) -> None:
    target = tmp_path / "state.txt"
    target.write_text("before\n", encoding="utf-8")
    store = FilesystemSnapshotStore()

    snapshot = store.create(tmp_path)
    target.write_text("after\n", encoding="utf-8")
    (tmp_path / "new.txt").write_text("extra\n", encoding="utf-8")

    with pytest.raises(PermissionError):
        store.restore(snapshot.id)
    assert target.read_text(encoding="utf-8") == "after\n"

    store.restore(snapshot.id, approval_granted=True)

    assert target.read_text(encoding="utf-8") == "before\n"
    assert not (tmp_path / "new.txt").exists()


def test_filesystem_snapshot_rejects_symlink_workspace_entry(tmp_path) -> None:
    real = tmp_path / "real"
    real.mkdir()
    (real / "data.txt").write_text("data", encoding="utf-8")
    (tmp_path / "link").symlink_to(real / "data.txt")
    store = FilesystemSnapshotStore()

    with pytest.raises(SnapshotError, match="symlink"):
        store.create(tmp_path)


def test_filesystem_snapshot_respects_disabled_restore_permission(tmp_path) -> None:
    permissions = PermissionEngine()
    store = FilesystemSnapshotStore(permissions=permissions)
    snapshot = store.create(tmp_path)

    permissions = PermissionEngine()
    denied_store = FilesystemSnapshotStore(permissions=permissions)
    denied_store._snapshots[snapshot.id] = snapshot

    with pytest.raises(PermissionError):
        denied_store.restore(snapshot.id)


def test_filesystem_snapshot_missing_workspace_is_rejected(tmp_path) -> None:
    store = FilesystemSnapshotStore()

    with pytest.raises(SnapshotError, match="does not exist"):
        store.create(Path(tmp_path) / "missing")
