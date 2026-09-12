from __future__ import annotations

import pytest

from core.workspace import InMemoryGitRunner
from core.workspace import LockState, WorkspaceError, WorkspaceKind, WorkspaceManager
from core.workspace import WorkspaceState, WorkspaceStore


def _setup(tmp_path):
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    root = tmp_path / "workspaces"
    root.mkdir()
    return repo, root


def test_scope_lock_heartbeat_and_optimistic_revision(tmp_path):
    repo, root = _setup(tmp_path)
    store = WorkspaceStore()
    manager = WorkspaceManager(store, root=root, git=InMemoryGitRunner())
    manager.create_workspace(
        tenant_id="tenant-a",
        project_id="project-a",
        owner_id="owner-a",
        repo_root=repo,
        workspace_id="ws-a",
        kind=WorkspaceKind.DIRECTORY,
    )

    with pytest.raises(WorkspaceError):
        manager.lock_state("ws-a", tenant_id="tenant-b", project_id="project-a")

    first = manager.acquire_lock(
        "ws-a",
        tenant_id="tenant-a",
        project_id="project-a",
        actor_id="owner-a",
        ttl_seconds=10,
    )
    with pytest.raises(WorkspaceError):
        manager.acquire_lock(
            "ws-a",
            tenant_id="tenant-a",
            project_id="project-a",
            actor_id="other",
        )
    second = manager.heartbeat_lock(
        "ws-a",
        tenant_id="tenant-a",
        project_id="project-a",
        actor_id="owner-a",
        ttl_seconds=20,
    )
    assert second.revision == first.revision + 1
    assert manager.lock_state(
        "ws-a", tenant_id="tenant-a", project_id="project-a"
    ) is LockState.HELD

    with pytest.raises(WorkspaceError):
        store.update(
            "ws-a",
            expected_revision=first.revision,
            actor_id="owner-a",
            state=WorkspaceState.DIRTY,
        )


def test_snapshot_rejects_symlinks_and_secret_metadata(tmp_path):
    repo, root = _setup(tmp_path)
    store = WorkspaceStore()
    manager = WorkspaceManager(store, root=root, git=InMemoryGitRunner())

    with pytest.raises(WorkspaceError):
        manager.create_workspace(
            tenant_id="t",
            project_id="p",
            owner_id="u",
            repo_root=repo,
            metadata={"api_key": "secret"},
        )

    manager.create_workspace(
        tenant_id="t",
        project_id="p",
        owner_id="u",
        repo_root=repo,
        workspace_id="ws",
        kind=WorkspaceKind.DIRECTORY,
    )
    path = root / "ws"
    path.mkdir()
    (path / "file.txt").write_text("safe")
    (path / "link").symlink_to(path / "file.txt")

    with pytest.raises(WorkspaceError):
        manager.snapshot(
            "ws",
            tenant_id="t",
            project_id="p",
            actor_id="u",
        )


def test_git_diff_artifact_branch_merge_preparation_and_lock_authorization(tmp_path):
    repo, root = _setup(tmp_path)
    git = InMemoryGitRunner()
    path = root / "ws"
    git.set(["git", "worktree", "add", "--force", "-b", "feature", str(path), "main"])
    git.set(
        ["git", "status", "--porcelain=v2", "--branch"],
        "1 .M N... 100644 100644 100644 a b file.txt\n",
    )
    git.set(
        ["git", "diff", "--binary"],
        "diff --git a/file.txt b/file.txt\n+new\n",
    )
    git.set(["git", "branch", "topic", "HEAD"])
    git.set(["git", "status", "--porcelain=v2"], "")
    git.set(["git", "rev-list", "--left-right", "--count", "main...HEAD"], "1\t2\n")
    git.set(["git", "rev-parse", "HEAD"], "head123\n")
    git.set(["git", "merge-base", "main", "HEAD"], "base123\n")
    git.set(["git", "diff", "--name-only", "main...HEAD"], "file.txt\n")

    store = WorkspaceStore()
    manager = WorkspaceManager(store, root=root, git=git)
    manager.create_workspace(
        tenant_id="t",
        project_id="p",
        owner_id="u",
        repo_root=repo,
        workspace_id="ws",
        branch="feature",
        base_ref="main",
    )
    manager.materialize("ws", tenant_id="t", project_id="p", actor_id="u")
    summary = manager.diff(
        "ws", tenant_id="t", project_id="p", actor_id="u"
    )
    assert summary.dirty
    assert summary.artifact_id
    assert manager.get_artifacts("ws", tenant_id="t", project_id="p")

    manager.create_branch(
        "ws",
        tenant_id="t",
        project_id="p",
        actor_id="u",
        branch="topic",
    )
    preparation = manager.prepare_merge(
        "ws", tenant_id="t", project_id="p", actor_id="u", target_ref="main"
    )
    assert preparation.ahead == 2
    assert preparation.behind == 1

    manager.acquire_lock("ws", tenant_id="t", project_id="p", actor_id="u")
    assert manager.authorize_merge(
        "ws",
        tenant_id="t",
        project_id="p",
        actor_id="u",
        approval="approval-1",
    )


def test_cleanup_and_gc_are_fail_closed(tmp_path):
    repo, root = _setup(tmp_path)
    store = WorkspaceStore()
    manager = WorkspaceManager(store, root=root, git=InMemoryGitRunner())
    manager.create_workspace(
        tenant_id="t",
        project_id="p",
        owner_id="u",
        repo_root=repo,
        workspace_id="ws",
        kind=WorkspaceKind.DIRECTORY,
    )
    with pytest.raises(WorkspaceError):
        manager.cleanup(
            "ws", tenant_id="t", project_id="p", actor_id="u", force=True
        )
    (root / "ws").mkdir()
    result = manager.cleanup("ws", tenant_id="t", project_id="p", actor_id="u")
    assert result.removed
    assert store.get("ws").state is WorkspaceState.ARCHIVED
    assert manager.gc(older_than_seconds=0, actor_id="gc", dry_run=True)
