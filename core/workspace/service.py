"""Durable, isolated workspace and worktree lifecycle service."""
from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
import time
import uuid
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from .models import (
    AuthorizationContext,
    CleanupResult,
    DiffSummary,
    LockState,
    MergePreparation,
    Workspace,
    WorkspaceArtifact,
    WorkspaceError,
    WorkspaceEvent,
    WorkspaceKind,
    WorkspaceSnapshot,
    WorkspaceState,
)
from .runner import GitError, GitRunner

MAX_SNAPSHOT_FILES = 20_000
MAX_SNAPSHOT_BYTES = 32 * 1024 * 1024
MAX_PATCH_BYTES = 512 * 1024
LOCK_TTL_SECONDS = 120.0
MAX_GC_BATCH = 1000
_SECRET_KEYS = {
    "authorization", "api_key", "credential", "password",
    "private_key", "secret", "token",
}


def _canonical(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"), sort_keys=True, ensure_ascii=False)


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _safe_path(base: Path, target: Path) -> bool:
    try:
        return target.resolve(strict=False).is_relative_to(base.resolve(strict=False))
    except OSError:
        return False


def _safe_mapping(value: Mapping[str, Any]) -> dict[str, Any]:
    def clean(item: Any, depth: int = 0) -> Any:
        if depth > 8:
            raise WorkspaceError("metadata nesting exceeds safety limit")
        if isinstance(item, Mapping):
            if len(item) > 64:
                raise WorkspaceError("metadata has too many keys")
            output: dict[str, Any] = {}
            for key, child in item.items():
                if not isinstance(key, str) or not key.strip():
                    raise WorkspaceError("metadata keys must be non-empty strings")
                if key.lower().replace("-", "_") in _SECRET_KEYS:
                    raise WorkspaceError("secret-like metadata rejected")
                output[key] = clean(child, depth + 1)
            return output
        if isinstance(item, (list, tuple)):
            if len(item) > 256:
                raise WorkspaceError("metadata list is too large")
            return [clean(child, depth + 1) for child in item]
        if isinstance(item, (str, int, float, bool)) or item is None:
            return item
        raise WorkspaceError("unsupported metadata value")

    return clean(value)


class WorkspaceStore:
    """SQLite-backed workspace state with tamper-evident event history."""

    def __init__(self, path: str | Path = ":memory:") -> None:
        self.path = str(path)
        self._db = sqlite3.connect(self.path, isolation_level=None, check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._db.execute("PRAGMA foreign_keys=ON")
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.executescript(
            """
            CREATE TABLE IF NOT EXISTS workspaces (
                workspace_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                project_id TEXT NOT NULL,
                owner_id TEXT NOT NULL,
                path TEXT NOT NULL,
                repo_root TEXT NOT NULL,
                kind TEXT NOT NULL,
                branch TEXT,
                base_ref TEXT,
                state TEXT NOT NULL,
                revision INTEGER NOT NULL,
                lock_owner TEXT,
                lock_expires_at REAL,
                metadata_json TEXT NOT NULL,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL,
                content_digest TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS ix_ws_scope
                ON workspaces(tenant_id, project_id, updated_at DESC);
            CREATE TABLE IF NOT EXISTS workspace_events (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                actor_id TEXT NOT NULL,
                revision INTEGER NOT NULL,
                payload_json TEXT NOT NULL,
                occurred_at REAL NOT NULL,
                digest TEXT NOT NULL,
                previous_digest TEXT,
                FOREIGN KEY(workspace_id) REFERENCES workspaces(workspace_id)
            );
            CREATE INDEX IF NOT EXISTS ix_ws_events
                ON workspace_events(workspace_id, sequence);
            CREATE TABLE IF NOT EXISTS snapshots (
                snapshot_id TEXT PRIMARY KEY,
                workspace_id TEXT NOT NULL,
                revision INTEGER NOT NULL,
                captured_at REAL NOT NULL,
                file_count INTEGER NOT NULL,
                byte_count INTEGER NOT NULL,
                digest TEXT NOT NULL,
                files_json TEXT NOT NULL,
                FOREIGN KEY(workspace_id) REFERENCES workspaces(workspace_id)
            );
            CREATE TABLE IF NOT EXISTS artifacts (
                artifact_id TEXT PRIMARY KEY,
                workspace_id TEXT NOT NULL,
                revision INTEGER NOT NULL,
                kind TEXT NOT NULL,
                media_type TEXT NOT NULL,
                size INTEGER NOT NULL,
                sha256 TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at REAL NOT NULL,
                FOREIGN KEY(workspace_id) REFERENCES workspaces(workspace_id)
            );
            CREATE INDEX IF NOT EXISTS ix_ws_artifacts
                ON artifacts(workspace_id, created_at DESC);
            """
        )

    def close(self) -> None:
        self._db.close()

    @staticmethod
    def _row(row: sqlite3.Row) -> Workspace:
        return Workspace(
            workspace_id=row["workspace_id"],
            tenant_id=row["tenant_id"],
            project_id=row["project_id"],
            owner_id=row["owner_id"],
            path=row["path"],
            repo_root=row["repo_root"],
            kind=WorkspaceKind(row["kind"]),
            branch=row["branch"],
            base_ref=row["base_ref"],
            state=WorkspaceState(row["state"]),
            revision=row["revision"],
            lock_owner=row["lock_owner"],
            lock_expires_at=row["lock_expires_at"],
            metadata=json.loads(row["metadata_json"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            content_digest=row["content_digest"],
        )

    def create(self, workspace: Workspace, actor_id: str) -> Workspace:
        with self._db:
            try:
                self._db.execute(
                    "INSERT INTO workspaces VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        workspace.workspace_id,
                        workspace.tenant_id,
                        workspace.project_id,
                        workspace.owner_id,
                        workspace.path,
                        workspace.repo_root,
                        workspace.kind.value,
                        workspace.branch,
                        workspace.base_ref,
                        workspace.state.value,
                        workspace.revision,
                        workspace.lock_owner,
                        workspace.lock_expires_at,
                        _canonical(dict(workspace.metadata)),
                        workspace.created_at,
                        workspace.updated_at,
                        workspace.content_digest,
                    ),
                )
            except sqlite3.IntegrityError as exc:
                raise WorkspaceError("workspace id already exists") from exc
        self.append_event(
            workspace.workspace_id,
            "workspace.created",
            actor_id,
            workspace.revision,
            {"kind": workspace.kind.value},
        )
        return workspace

    def get(self, workspace_id: str) -> Workspace:
        row = self._db.execute(
            "SELECT * FROM workspaces WHERE workspace_id=?", (workspace_id,)
        ).fetchone()
        if row is None:
            raise WorkspaceError(f"workspace {workspace_id} not found")
        return self._row(row)

    def get_scoped(self, workspace_id: str, tenant_id: str, project_id: str) -> Workspace:
        workspace = self.get(workspace_id)
        if workspace.tenant_id != tenant_id or workspace.project_id != project_id:
            raise WorkspaceError("workspace is outside caller scope")
        return workspace

    def list(self, tenant_id: str, project_id: str, limit: int = 1000) -> tuple[Workspace, ...]:
        limit = max(1, min(limit, 1000))
        rows = self._db.execute(
            "SELECT * FROM workspaces WHERE tenant_id=? AND project_id=? "
            "ORDER BY updated_at DESC, workspace_id LIMIT ?",
            (tenant_id, project_id, limit),
        ).fetchall()
        return tuple(self._row(row) for row in rows)

    def append_event(
        self,
        workspace_id: str,
        event_type: str,
        actor_id: str,
        revision: int,
        payload: Mapping[str, Any],
    ) -> WorkspaceEvent:
        safe_payload = _safe_mapping(payload)
        previous = self._db.execute(
            "SELECT digest FROM workspace_events WHERE workspace_id=? "
            "ORDER BY sequence DESC LIMIT 1",
            (workspace_id,),
        ).fetchone()
        previous_digest = previous["digest"] if previous else None
        occurred_at = time.time()
        envelope = {
            "workspace_id": workspace_id,
            "event_type": event_type,
            "actor_id": actor_id,
            "revision": revision,
            "payload": safe_payload,
            "occurred_at": occurred_at,
            "previous_digest": previous_digest,
        }
        digest = _digest(envelope)
        cursor = self._db.execute(
            "INSERT INTO workspace_events(workspace_id,event_type,actor_id,revision,"
            "payload_json,occurred_at,digest,previous_digest) VALUES(?,?,?,?,?,?,?,?)",
            (
                workspace_id,
                event_type,
                actor_id,
                revision,
                _canonical(safe_payload),
                occurred_at,
                digest,
                previous_digest,
            ),
        )
        return WorkspaceEvent(
            cursor.lastrowid,
            workspace_id,
            event_type,
            actor_id,
            revision,
            safe_payload,
            occurred_at,
            digest,
            previous_digest,
        )

    def events(self, workspace_id: str) -> tuple[WorkspaceEvent, ...]:
        rows = self._db.execute(
            "SELECT * FROM workspace_events WHERE workspace_id=? ORDER BY sequence",
            (workspace_id,),
        ).fetchall()
        return tuple(
            WorkspaceEvent(
                row["sequence"],
                row["workspace_id"],
                row["event_type"],
                row["actor_id"],
                row["revision"],
                json.loads(row["payload_json"]),
                row["occurred_at"],
                row["digest"],
                row["previous_digest"],
            )
            for row in rows
        )

    def verify_event_chain(self, workspace_id: str) -> bool:
        previous_digest = None
        for event in self.events(workspace_id):
            envelope = {
                "workspace_id": event.workspace_id,
                "event_type": event.event_type,
                "actor_id": event.actor_id,
                "revision": event.revision,
                "payload": dict(event.payload),
                "occurred_at": event.occurred_at,
                "previous_digest": previous_digest,
            }
            if event.previous_digest != previous_digest or event.digest != _digest(envelope):
                return False
            previous_digest = event.digest
        return True

    def update(
        self,
        workspace_id: str,
        *,
        expected_revision: int,
        actor_id: str,
        **changes: Any,
    ) -> Workspace:
        current = self.get(workspace_id)
        if current.revision != expected_revision:
            raise WorkspaceError("stale workspace revision")
        values = {
            "workspace_id": current.workspace_id,
            "tenant_id": current.tenant_id,
            "project_id": current.project_id,
            "owner_id": current.owner_id,
            "path": current.path,
            "repo_root": current.repo_root,
            "kind": current.kind,
            "branch": current.branch,
            "base_ref": current.base_ref,
            "state": current.state,
            "revision": expected_revision + 1,
            "lock_owner": current.lock_owner,
            "lock_expires_at": current.lock_expires_at,
            "metadata": dict(current.metadata),
            "created_at": current.created_at,
            "updated_at": time.time(),
            "content_digest": current.content_digest,
        }
        values.update(changes)
        values["metadata"] = _safe_mapping(values["metadata"])
        workspace = Workspace(**values)
        with self._db:
            changed = self._db.execute(
                "UPDATE workspaces SET branch=?,base_ref=?,state=?,revision=?,"
                "lock_owner=?,lock_expires_at=?,metadata_json=?,updated_at=?,content_digest=? "
                "WHERE workspace_id=? AND revision=?",
                (
                    workspace.branch,
                    workspace.base_ref,
                    workspace.state.value,
                    workspace.revision,
                    workspace.lock_owner,
                    workspace.lock_expires_at,
                    _canonical(dict(workspace.metadata)),
                    workspace.updated_at,
                    workspace.content_digest,
                    workspace_id,
                    expected_revision,
                ),
            ).rowcount
            if changed != 1:
                raise WorkspaceError("workspace changed concurrently")
        self.append_event(
            workspace_id,
            "workspace.updated",
            actor_id,
            workspace.revision,
            {"changes": sorted(changes)},
        )
        return workspace

    def snapshot(self, snapshot: WorkspaceSnapshot) -> None:
        self._db.execute(
            "INSERT INTO snapshots VALUES(?,?,?,?,?,?,?,?)",
            (
                snapshot.snapshot_id,
                snapshot.workspace_id,
                snapshot.revision,
                snapshot.captured_at,
                snapshot.file_count,
                snapshot.byte_count,
                snapshot.digest,
                _canonical(snapshot.files),
            ),
        )

    def snapshots(self, workspace_id: str) -> tuple[WorkspaceSnapshot, ...]:
        rows = self._db.execute(
            "SELECT * FROM snapshots WHERE workspace_id=? ORDER BY captured_at",
            (workspace_id,),
        ).fetchall()
        return tuple(
            WorkspaceSnapshot(
                row["snapshot_id"],
                row["workspace_id"],
                row["revision"],
                row["captured_at"],
                row["file_count"],
                row["byte_count"],
                row["digest"],
                tuple(tuple(item) for item in json.loads(row["files_json"])),
            )
            for row in rows
        )

    def artifact(self, artifact: WorkspaceArtifact) -> None:
        self._db.execute(
            "INSERT INTO artifacts VALUES(?,?,?,?,?,?,?,?,?)",
            (
                artifact.artifact_id,
                artifact.workspace_id,
                artifact.revision,
                artifact.kind,
                artifact.media_type,
                artifact.size,
                artifact.sha256,
                artifact.content,
                artifact.created_at,
            ),
        )

    def artifacts(self, workspace_id: str) -> tuple[WorkspaceArtifact, ...]:
        rows = self._db.execute(
            "SELECT * FROM artifacts WHERE workspace_id=? ORDER BY created_at",
            (workspace_id,),
        ).fetchall()
        return tuple(
            WorkspaceArtifact(
                row["artifact_id"],
                row["workspace_id"],
                row["revision"],
                row["kind"],
                row["media_type"],
                row["size"],
                row["sha256"],
                row["content"],
                row["created_at"],
            )
            for row in rows
        )

    def gc_candidates(self, older_than: float, limit: int = MAX_GC_BATCH) -> tuple[Workspace, ...]:
        rows = self._db.execute(
            "SELECT * FROM workspaces WHERE state IN (?,?) AND updated_at<? "
            "ORDER BY updated_at LIMIT ?",
            (
                WorkspaceState.ARCHIVED.value,
                WorkspaceState.RECOVERY_REQUIRED.value,
                older_than,
                max(1, min(limit, MAX_GC_BATCH)),
            ),
        ).fetchall()
        return tuple(self._row(row) for row in rows)


class WorkspaceManager:
    """Isolation-first lifecycle orchestration; adapters never become authorities."""

    def __init__(
        self,
        store: WorkspaceStore,
        *,
        root: str | Path,
        git: GitRunner | None = None,
        authorize: Callable[[AuthorizationContext], bool] | None = None,
    ) -> None:
        self.store = store
        self.root = Path(root).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.git = git
        self.authorize = authorize

    def _check_auth(
        self,
        workspace: Workspace,
        actor_id: str,
        action: str,
        resource: str,
        approval: str | None = None,
    ) -> None:
        if self.authorize is None:
            return
        context = AuthorizationContext(
            actor_id,
            workspace.tenant_id,
            workspace.project_id,
            action,
            resource,
            approval,
        )
        if not self.authorize(context):
            raise WorkspaceError(f"authorization denied: {action}")

    def _runner(self) -> GitRunner:
        if self.git is None:
            raise WorkspaceError("Git execution adapter is not configured")
        return self.git

    def _get(self, workspace_id: str, tenant_id: str, project_id: str) -> Workspace:
        return self.store.get_scoped(workspace_id, tenant_id, project_id)

    def create_workspace(
        self,
        *,
        tenant_id: str,
        project_id: str,
        owner_id: str,
        repo_root: str | Path,
        branch: str | None = None,
        base_ref: str | None = None,
        kind: WorkspaceKind = WorkspaceKind.GIT_WORKTREE,
        workspace_id: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> Workspace:
        repo = Path(repo_root).expanduser().resolve()
        if not repo.is_dir():
            raise WorkspaceError("repo root must be an existing directory")
        if kind is WorkspaceKind.GIT_WORKTREE and not (repo / ".git").exists():
            raise WorkspaceError("Git worktree requires a Git repository")
        workspace_id = workspace_id or f"ws_{uuid.uuid4().hex}"
        path = (self.root / workspace_id).resolve()
        if not _safe_path(self.root, path):
            raise WorkspaceError("workspace path escaped workspace root")
        workspace = Workspace(
            workspace_id=workspace_id,
            tenant_id=tenant_id,
            project_id=project_id,
            owner_id=owner_id,
            path=str(path),
            repo_root=str(repo),
            kind=kind,
            branch=branch,
            base_ref=base_ref,
            metadata=_safe_mapping(dict(metadata or {})),
        )
        return self.store.create(workspace, owner_id)

    def materialize(
        self,
        workspace_id: str,
        *,
        tenant_id: str,
        project_id: str,
        actor_id: str,
    ) -> Workspace:
        workspace = self._get(workspace_id, tenant_id, project_id)
        self._check_auth(
            workspace,
            actor_id,
            "workspace.materialize",
            workspace.path,
        )
        path = Path(workspace.path)
        if not _safe_path(self.root, path) or path.is_symlink():
            raise WorkspaceError("workspace path is unsafe")
        path.parent.mkdir(parents=True, exist_ok=True)
        if workspace.kind is WorkspaceKind.DIRECTORY:
            path.mkdir(parents=True, exist_ok=True)
        else:
            if path.exists() and any(path.iterdir()):
                raise WorkspaceError("workspace path is not empty")
            runner = self._runner()
            args = ["git", "worktree", "add", "--force"]
            if workspace.branch:
                args.extend(["-b", workspace.branch])
            args.extend([str(path), workspace.base_ref or "HEAD"])
            try:
                runner.run(args, cwd=Path(workspace.repo_root))
            except GitError as exc:
                self.store.update(
                    workspace_id,
                    expected_revision=workspace.revision,
                    actor_id=actor_id,
                    state=WorkspaceState.RECOVERY_REQUIRED,
                )
                raise WorkspaceError(str(exc)) from exc
        self.store.append_event(
            workspace_id,
            "workspace.materialized",
            actor_id,
            workspace.revision,
            {"path": workspace.path},
        )
        return self.store.get(workspace_id)

    def acquire_lock(
        self,
        workspace_id: str,
        *,
        tenant_id: str,
        project_id: str,
        actor_id: str,
        ttl_seconds: float = LOCK_TTL_SECONDS,
    ) -> Workspace:
        workspace = self._get(workspace_id, tenant_id, project_id)
        self._check_auth(workspace, actor_id, "workspace.lock", workspace.path)
        if ttl_seconds <= 0 or ttl_seconds > 3600:
            raise WorkspaceError("invalid lock TTL")
        now = time.time()
        if (
            workspace.lock_owner
            and (workspace.lock_expires_at or 0) > now
            and workspace.lock_owner != actor_id
        ):
            raise WorkspaceError("workspace is already locked")
        return self.store.update(
            workspace_id,
            expected_revision=workspace.revision,
            actor_id=actor_id,
            lock_owner=actor_id,
            lock_expires_at=now + ttl_seconds,
        )

    def heartbeat_lock(
        self,
        workspace_id: str,
        *,
        tenant_id: str,
        project_id: str,
        actor_id: str,
        ttl_seconds: float = LOCK_TTL_SECONDS,
    ) -> Workspace:
        workspace = self._get(workspace_id, tenant_id, project_id)
        if workspace.lock_owner != actor_id:
            raise WorkspaceError("only the lock owner may heartbeat")
        if self.lock_state(
            workspace_id,
            tenant_id=tenant_id,
            project_id=project_id,
        ) is not LockState.HELD:
            raise WorkspaceError("lock is not live")
        if ttl_seconds <= 0 or ttl_seconds > 3600:
            raise WorkspaceError("invalid lock TTL")
        return self.store.update(
            workspace_id,
            expected_revision=workspace.revision,
            actor_id=actor_id,
            lock_expires_at=time.time() + ttl_seconds,
        )

    def lock_state(self, workspace_id: str, *, tenant_id: str, project_id: str) -> LockState:
        workspace = self._get(workspace_id, tenant_id, project_id)
        if workspace.lock_owner is None:
            return LockState.FREE
        return (
            LockState.HELD
            if (workspace.lock_expires_at or 0) > time.time()
            else LockState.EXPIRED
        )

    def release_lock(
        self,
        workspace_id: str,
        *,
        tenant_id: str,
        project_id: str,
        actor_id: str,
    ) -> Workspace:
        workspace = self._get(workspace_id, tenant_id, project_id)
        if workspace.lock_owner != actor_id and self.lock_state(
            workspace_id,
            tenant_id=tenant_id,
            project_id=project_id,
        ) is LockState.HELD:
            raise WorkspaceError("only the lock owner may release")
        return self.store.update(
            workspace_id,
            expected_revision=workspace.revision,
            actor_id=actor_id,
            lock_owner=None,
            lock_expires_at=None,
        )

    def create_branch(
        self,
        workspace_id: str,
        *,
        tenant_id: str,
        project_id: str,
        actor_id: str,
        branch: str,
        base_ref: str | None = None,
    ) -> Workspace:
        workspace = self._get(workspace_id, tenant_id, project_id)
        self._check_auth(workspace, actor_id, "workspace.branch.create", branch)
        if (
            not branch
            or branch.startswith("-")
            or ".." in branch
            or "\x00" in branch
            or " " in branch
        ):
            raise WorkspaceError("invalid branch name")
        self._runner().run(
            ["git", "branch", branch, base_ref or "HEAD"],
            cwd=Path(workspace.repo_root),
        )
        return self.store.update(
            workspace_id,
            expected_revision=workspace.revision,
            actor_id=actor_id,
            branch=branch,
            base_ref=base_ref or "HEAD",
        )

    def snapshot(
        self,
        workspace_id: str,
        *,
        tenant_id: str,
        project_id: str,
        actor_id: str,
    ) -> WorkspaceSnapshot:
        workspace = self._get(workspace_id, tenant_id, project_id)
        self._check_auth(workspace, actor_id, "workspace.snapshot", workspace.path)
        base = Path(workspace.path)
        if not _safe_path(self.root, base) or not base.exists():
            raise WorkspaceError("workspace path is unavailable")
        files: list[tuple[str, str, int]] = []
        total_bytes = 0
        for path in sorted(base.rglob("*")):
            if ".git" in path.parts:
                continue
            if not path.is_file():
                continue
            if path.is_symlink():
                raise WorkspaceError("symlink inside workspace is not snapshot-safe")
            if len(files) >= MAX_SNAPSHOT_FILES:
                raise WorkspaceError("snapshot file limit exceeded")
            data = path.read_bytes()
            total_bytes += len(data)
            if total_bytes > MAX_SNAPSHOT_BYTES:
                raise WorkspaceError("snapshot byte limit exceeded")
            relative = path.relative_to(base).as_posix()
            files.append((relative, hashlib.sha256(data).hexdigest(), len(data)))
        file_tuple = tuple(files)
        snapshot = WorkspaceSnapshot(
            snapshot_id=f"snap_{uuid.uuid4().hex}",
            workspace_id=workspace_id,
            revision=workspace.revision,
            captured_at=time.time(),
            file_count=len(file_tuple),
            byte_count=total_bytes,
            digest=_digest(file_tuple),
            files=file_tuple,
        )
        self.store.snapshot(snapshot)
        self.store.update(
            workspace_id,
            expected_revision=workspace.revision,
            actor_id=actor_id,
            content_digest=snapshot.digest,
        )
        return snapshot

    def diff(
        self,
        workspace_id: str,
        *,
        tenant_id: str,
        project_id: str,
        actor_id: str,
    ) -> DiffSummary:
        workspace = self._get(workspace_id, tenant_id, project_id)
        self._check_auth(workspace, actor_id, "workspace.diff", workspace.path)
        if workspace.kind is WorkspaceKind.DIRECTORY:
            return DiffSummary(workspace_id, workspace.revision, 0, 0, 0, 0, False, False)
        runner = self._runner()
        try:
            status = runner.run(
                ["git", "status", "--porcelain=v2", "--branch"],
                cwd=Path(workspace.path),
            )
            patch = runner.run(["git", "diff", "--binary"], cwd=Path(workspace.path))
        except GitError as exc:
            raise WorkspaceError(str(exc)) from exc
        patch_bytes = patch.encode("utf-8")
        if len(patch_bytes) > MAX_PATCH_BYTES:
            raise WorkspaceError("diff exceeds artifact limit")
        status_lines = status.splitlines()
        changed = sum(
            1 for line in status_lines if line.startswith(("1 ", "2 ", "u "))
        )
        conflict = any(line.startswith("u ") for line in status_lines)
        additions = sum(
            1
            for line in patch.splitlines()
            if line.startswith("+") and not line.startswith("+++")
        )
        deletions = sum(
            1
            for line in patch.splitlines()
            if line.startswith("-") and not line.startswith("---")
        )
        binary = sum(1 for line in patch.splitlines() if line.startswith("Binary files"))
        dirty = bool(changed or patch)
        state = (
            WorkspaceState.CONFLICT
            if conflict
            else WorkspaceState.DIRTY
            if dirty
            else WorkspaceState.ACTIVE
        )
        updated = self.store.update(
            workspace_id,
            expected_revision=workspace.revision,
            actor_id=actor_id,
            state=state,
        )
        artifact_id = None
        if patch:
            digest = _digest(patch)
            artifact = WorkspaceArtifact(
                artifact_id=f"art_{uuid.uuid4().hex}",
                workspace_id=workspace_id,
                revision=updated.revision,
                kind="git-diff",
                media_type="text/x-diff",
                size=len(patch_bytes),
                sha256=digest,
                content=patch,
                created_at=time.time(),
            )
            self.store.artifact(artifact)
            artifact_id = artifact.artifact_id
        return DiffSummary(
            workspace_id,
            updated.revision,
            changed,
            additions,
            deletions,
            binary,
            dirty,
            conflict,
            patch,
            _digest(patch),
            artifact_id,
        )

    def get_artifacts(
        self,
        workspace_id: str,
        *,
        tenant_id: str,
        project_id: str,
    ) -> tuple[WorkspaceArtifact, ...]:
        self._get(workspace_id, tenant_id, project_id)
        return self.store.artifacts(workspace_id)

    def prepare_merge(
        self,
        workspace_id: str,
        *,
        tenant_id: str,
        project_id: str,
        actor_id: str,
        target_ref: str,
    ) -> MergePreparation:
        workspace = self._get(workspace_id, tenant_id, project_id)
        self._check_auth(
            workspace,
            actor_id,
            "workspace.merge.prepare",
            target_ref,
        )
        runner = self._runner()
        try:
            status = runner.run(
                ["git", "status", "--porcelain=v2"],
                cwd=Path(workspace.path),
            )
            counts = runner.run(
                [
                    "git",
                    "rev-list",
                    "--left-right",
                    "--count",
                    f"{target_ref}...HEAD",
                ],
                cwd=Path(workspace.path),
            ).strip()
            head = runner.run(["git", "rev-parse", "HEAD"], cwd=Path(workspace.path)).strip()
            base = runner.run(
                ["git", "merge-base", target_ref, "HEAD"],
                cwd=Path(workspace.path),
            ).strip()
            changed = runner.run(
                ["git", "diff", "--name-only", f"{target_ref}...HEAD"],
                cwd=Path(workspace.path),
            ).splitlines()
        except GitError as exc:
            raise WorkspaceError(str(exc)) from exc
        parts = counts.split()
        if len(parts) != 2:
            raise WorkspaceError("invalid Git ahead/behind response")
        behind, ahead = map(int, parts)
        conflicts = tuple(line for line in status.splitlines() if line.startswith("u "))
        clean = not status.strip()
        return MergePreparation(
            workspace_id,
            target_ref,
            base,
            head,
            clean,
            ahead,
            behind,
            len(changed),
            conflicts,
            "ready" if clean else "workspace is dirty",
        )

    def authorize_merge(
        self,
        workspace_id: str,
        *,
        tenant_id: str,
        project_id: str,
        actor_id: str,
        approval: str,
    ) -> Workspace:
        workspace = self._get(workspace_id, tenant_id, project_id)
        self._check_auth(
            workspace,
            actor_id,
            "workspace.merge",
            workspace.path,
            approval,
        )
        if not approval.strip():
            raise WorkspaceError("merge approval is required")
        if self.lock_state(
            workspace_id,
            tenant_id=tenant_id,
            project_id=project_id,
        ) is not LockState.HELD or workspace.lock_owner != actor_id:
            raise WorkspaceError("merge authorization requires a caller-owned live lock")
        return workspace

    def resume_from_snapshot(
        self,
        workspace_id: str,
        *,
        tenant_id: str,
        project_id: str,
        actor_id: str,
        snapshot_id: str,
        approval: str,
    ) -> Workspace:
        workspace = self._get(workspace_id, tenant_id, project_id)
        self._check_auth(workspace, actor_id, "workspace.resume", workspace.path, approval)
        if not approval.strip():
            raise WorkspaceError("resume approval is required")
        if not any(s.snapshot_id == snapshot_id for s in self.store.snapshots(workspace_id)):
            raise WorkspaceError("snapshot not found")
        return self.store.update(
            workspace_id,
            expected_revision=workspace.revision,
            actor_id=actor_id,
            state=WorkspaceState.ACTIVE,
            metadata={**dict(workspace.metadata), "resumed_from": snapshot_id},
        )

    def cleanup(
        self,
        workspace_id: str,
        *,
        tenant_id: str,
        project_id: str,
        actor_id: str,
        force: bool = False,
        approval: str | None = None,
    ) -> CleanupResult:
        workspace = self._get(workspace_id, tenant_id, project_id)
        self._check_auth(workspace, actor_id, "workspace.cleanup", workspace.path, approval)
        if self.lock_state(
            workspace_id,
            tenant_id=tenant_id,
            project_id=project_id,
        ) is LockState.HELD and workspace.lock_owner != actor_id:
            raise WorkspaceError("cannot cleanup another actor's live lock")
        if force and not approval:
            raise WorkspaceError("forced cleanup requires approval")
        if not force:
            summary = self.diff(
                workspace_id,
                tenant_id=tenant_id,
                project_id=project_id,
                actor_id=actor_id,
            )
            if summary.dirty or summary.conflict:
                raise WorkspaceError("refusing to delete dirty/conflicted workspace")
        pending = self.store.update(
            workspace_id,
            expected_revision=workspace.revision,
            actor_id=actor_id,
            state=WorkspaceState.CLEANUP_PENDING,
            lock_owner=None,
            lock_expires_at=None,
        )
        path = Path(pending.path)
        try:
            if not _safe_path(self.root, path) or path.resolve() == self.root.resolve():
                raise WorkspaceError("unsafe cleanup path")
            if path.is_symlink():
                raise WorkspaceError("refusing symlink cleanup")
            if (
                pending.kind is WorkspaceKind.GIT_WORKTREE
                and path.exists()
            ):
                self._runner().run(
                    ["git", "worktree", "remove", "--force", str(path)],
                    cwd=Path(pending.repo_root),
                )
            if path.exists():
                shutil.rmtree(path)
            final = self.store.update(
                workspace_id,
                expected_revision=pending.revision,
                actor_id=actor_id,
                state=WorkspaceState.ARCHIVED,
            )
            return CleanupResult(workspace_id, True, False, final.revision, "cleaned")
        except Exception as exc:
            try:
                self.store.update(
                    workspace_id,
                    expected_revision=pending.revision,
                    actor_id=actor_id,
                    state=WorkspaceState.RECOVERY_REQUIRED,
                )
            except WorkspaceError:
                pass
            if isinstance(exc, WorkspaceError):
                raise
            return CleanupResult(
                workspace_id,
                False,
                True,
                self.store.get(workspace_id).revision,
                "cleanup requires recovery",
            )

    def gc(
        self,
        *,
        older_than_seconds: float,
        actor_id: str,
        limit: int = 100,
        dry_run: bool = True,
    ) -> tuple[CleanupResult, ...]:
        if older_than_seconds < 0:
            raise WorkspaceError("older_than_seconds must be non-negative")
        candidates = self.store.gc_candidates(
            time.time() - older_than_seconds,
            min(limit, MAX_GC_BATCH),
        )
        if dry_run:
            return tuple(
                CleanupResult(w.workspace_id, False, False, w.revision, "candidate")
                for w in candidates
            )
        results: list[CleanupResult] = []
        for workspace in candidates:
            try:
                results.append(
                    self.cleanup(
                        workspace.workspace_id,
                        tenant_id=workspace.tenant_id,
                        project_id=workspace.project_id,
                        actor_id=actor_id,
                        force=True,
                        approval="gc",
                    )
                )
            except WorkspaceError as exc:
                results.append(
                    CleanupResult(
                        workspace.workspace_id,
                        False,
                        True,
                        self.store.get(workspace.workspace_id).revision,
                        str(exc),
                    )
                )
        return tuple(results)
