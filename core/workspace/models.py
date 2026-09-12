"""Phase 58 workspace and worktree lifecycle contracts."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Mapping

MAX_ID_LENGTH = 128
MAX_METADATA_KEYS = 64


class WorkspaceKind(StrEnum):
    GIT_WORKTREE = "git_worktree"
    DIRECTORY = "directory"


class WorkspaceState(StrEnum):
    ACTIVE = "active"
    DIRTY = "dirty"
    CONFLICT = "conflict"
    CLEANUP_PENDING = "cleanup_pending"
    ARCHIVED = "archived"
    RECOVERY_REQUIRED = "recovery_required"


class LockState(StrEnum):
    FREE = "free"
    HELD = "held"
    EXPIRED = "expired"


class WorkspaceError(ValueError):
    """Workspace contract violation or lifecycle failure."""


@dataclass(frozen=True, slots=True)
class Workspace:
    workspace_id: str
    tenant_id: str
    project_id: str
    owner_id: str
    path: str
    repo_root: str
    kind: WorkspaceKind = WorkspaceKind.GIT_WORKTREE
    branch: str | None = None
    base_ref: str | None = None
    state: WorkspaceState = WorkspaceState.ACTIVE
    revision: int = 1
    lock_owner: str | None = None
    lock_expires_at: float | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=lambda: datetime.now(UTC).timestamp())
    updated_at: float = field(default_factory=lambda: datetime.now(UTC).timestamp())
    content_digest: str = ""

    def __post_init__(self) -> None:
        for name, value in (
            ("workspace_id", self.workspace_id),
            ("tenant_id", self.tenant_id),
            ("project_id", self.project_id),
            ("owner_id", self.owner_id),
            ("path", self.path),
            ("repo_root", self.repo_root),
        ):
            if not isinstance(value, str) or not value.strip() or len(value) > MAX_ID_LENGTH:
                raise WorkspaceError(f"{name} is required and bounded")
        if self.revision < 1:
            raise WorkspaceError("revision must be positive")
        if len(self.metadata) > MAX_METADATA_KEYS:
            raise WorkspaceError("workspace metadata has too many keys")
        if any(not isinstance(key, str) or not key.strip() for key in self.metadata):
            raise WorkspaceError("workspace metadata keys must be non-empty strings")
        if self.lock_owner is None and self.lock_expires_at is not None:
            raise WorkspaceError("lock expiry requires lock owner")
        if self.lock_owner is not None and self.lock_expires_at is None:
            raise WorkspaceError("lock owner requires lock expiry")


@dataclass(frozen=True, slots=True)
class WorkspaceEvent:
    sequence: int
    workspace_id: str
    event_type: str
    actor_id: str
    revision: int
    payload: Mapping[str, Any]
    occurred_at: float
    digest: str
    previous_digest: str | None


@dataclass(frozen=True, slots=True)
class WorkspaceSnapshot:
    snapshot_id: str
    workspace_id: str
    revision: int
    captured_at: float
    file_count: int
    byte_count: int
    digest: str
    files: tuple[tuple[str, str, int], ...]


@dataclass(frozen=True, slots=True)
class WorkspaceArtifact:
    artifact_id: str
    workspace_id: str
    revision: int
    kind: str
    media_type: str
    size: int
    sha256: str
    content: str
    created_at: float


@dataclass(frozen=True, slots=True)
class DiffSummary:
    workspace_id: str
    revision: int
    changed_files: int
    additions: int
    deletions: int
    binary_files: int
    dirty: bool
    conflict: bool
    patch: str = ""
    patch_digest: str = ""
    artifact_id: str | None = None


@dataclass(frozen=True, slots=True)
class MergePreparation:
    workspace_id: str
    target_ref: str
    base_ref: str
    head_ref: str
    clean: bool
    ahead: int
    behind: int
    changed_files: int
    conflicts: tuple[str, ...] = ()
    reason: str = ""


@dataclass(frozen=True, slots=True)
class AuthorizationContext:
    actor_id: str
    tenant_id: str
    project_id: str
    action: str
    resource: str
    approval: str | None = None


@dataclass(frozen=True, slots=True)
class CleanupResult:
    workspace_id: str
    removed: bool
    recovered: bool
    revision: int
    reason: str
