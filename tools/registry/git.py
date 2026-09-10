from __future__ import annotations

import subprocess
from pathlib import Path

from tools.registry.contracts import ToolResult


class GitTool:
    """Read-oriented Git adapter; mutations require explicit command execution policy."""

    def __init__(self, workspace: str | Path) -> None:
        self.workspace = Path(workspace).resolve()
        if not self.workspace.is_dir():
            raise ValueError(f"Workspace does not exist: {self.workspace}")

    def run(self, args: tuple[str, ...]) -> ToolResult:
        if not args:
            return ToolResult(False, error="Git arguments must not be empty")
        try:
            completed = subprocess.run(
                ["git", *args], cwd=self.workspace, capture_output=True, text=True, check=False
            )
        except OSError as exc:
            return ToolResult(False, error=str(exc))
        return ToolResult(
            completed.returncode == 0,
            value=completed.stdout,
            error=completed.stderr,
        )

    def status(self) -> ToolResult:
        return self.run(("status", "--short", "--branch"))

    def diff(self) -> ToolResult:
        return self.run(("diff", "--"))

    def log(self, limit: int = 20) -> ToolResult:
        if limit <= 0:
            raise ValueError("Log limit must be greater than zero")
        return self.run(("log", f"-{limit}", "--oneline", "--decorate"))
