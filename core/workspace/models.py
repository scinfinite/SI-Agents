"""Phase 58 workspace contracts."""
from enum import StrEnum
class WorkspaceKind(StrEnum):
    GIT_WORKTREE = "git_worktree"
    DIRECTORY = "directory"
