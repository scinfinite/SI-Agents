from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from tools.registry.contracts import ToolResult


class CommandTool:
    """Workspace-scoped adapter for developer tooling such as compilers and test runners."""

    def __init__(self, workspace: str | Path) -> None:
        self.workspace = Path(workspace).resolve()
        if not self.workspace.is_dir():
            raise ValueError(f"Workspace does not exist: {self.workspace}")

    def available(self, executable: str) -> bool:
        return bool(shutil.which(executable))

    def run(self, argv: tuple[str, ...], *, timeout: float = 120.0) -> ToolResult:
        if not argv or not argv[0].strip():
            raise ValueError("Command arguments must not be empty")
        if timeout <= 0:
            raise ValueError("Timeout must be greater than zero")
        try:
            completed = subprocess.run(
                list(argv), cwd=self.workspace, capture_output=True, text=True,
                timeout=timeout, check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return ToolResult(False, error=str(exc))
        return ToolResult(completed.returncode == 0, completed.stdout, completed.stderr)


class TestRunnerTool(CommandTool):
    def pytest(self, *args: str, timeout: float = 120.0) -> ToolResult:
        return self.run(("python", "-m", "pytest", *args), timeout=timeout)


class LinterTool(CommandTool):
    def ruff(self, *args: str, timeout: float = 120.0) -> ToolResult:
        return self.run(("python", "-m", "ruff", *args), timeout=timeout)


class FormatterTool(CommandTool):
    def ruff_format_check(self, *args: str, timeout: float = 120.0) -> ToolResult:
        return self.run(("python", "-m", "ruff", "format", "--check", *args), timeout=timeout)


class CompilerTool(CommandTool):
    def python_compile(self, *paths: str, timeout: float = 120.0) -> ToolResult:
        return self.run(("python", "-m", "compileall", *paths), timeout=timeout)


class PackageManagerTool(CommandTool):
    def pip_check(self, timeout: float = 120.0) -> ToolResult:
        return self.run(("python", "-m", "pip", "check"), timeout=timeout)
