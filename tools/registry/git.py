from __future__ import annotations

import subprocess
from pathlib import Path

from tools.registry.contracts import ToolResult


class GitTool:
    """Read-oriented Git adapter; repository mutations require a separate approved executor."""

    _MUTATING_COMMANDS = frozenset({
        "add", "am", "apply", "branch", "checkout", "cherry-pick", "clean", "commit",
        "config", "fetch", "merge", "mv", "pull", "push", "rebase", "reset", "restore",
        "rm", "switch", "tag", "worktree",
    })

    def __init__(self, workspace: str | Path) -> None:
        self.workspace = Path(workspace).resolve()
        if not self.workspace.is_dir():
            raise ValueError(f"Workspace does not exist: {self.workspace}")

    def run(self, args: tuple[str, ...]) -> ToolResult:
        if not args:
            return ToolResult(False, error="Git arguments must not be empty")
        if args[0] in self._MUTATING_COMMANDS:
            return ToolResult(False, error=f"Git mutation requires approved command execution: {args[0]}")
        try:
            completed = subprocess.run(
                ["git", *args], cwd=self.workspace, capture_output=True, text=True, check=False
            )
        except OSError as exc:
            return ToolResult(False, error=str(exc))
        return ToolResult(completed.returncode == 0, completed.stdout, completed.stderr)

    def status(self) -> ToolResult:
        return self.run(("status", "--short", "--branch"))

    def diff(self) -> ToolResult:
        return self.run(("diff", "--"))

    def log(self, limit: int = 20) -> ToolResult:
        if limit <= 0:
            raise ValueError("Log limit must be greater than zero")
        return self.run(("log", f"-{limit}", "--oneline", "--decorate"))
