"""Phase 58 workspace and worktree lifecycle authority."""
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
from .runner import CallableGitRunner, GitError, GitRunner, InMemoryGitRunner
from .service import WorkspaceManager, WorkspaceStore

__all__ = [
    "AuthorizationContext",
    "CallableGitRunner",
    "CleanupResult",
    "DiffSummary",
    "GitError",
    "GitRunner",
    "InMemoryGitRunner",
    "LockState",
    "MergePreparation",
    "Workspace",
    "WorkspaceArtifact",
    "WorkspaceError",
    "WorkspaceEvent",
    "WorkspaceKind",
    "WorkspaceManager",
    "WorkspaceSnapshot",
    "WorkspaceState",
    "WorkspaceStore",
]
