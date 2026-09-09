from __future__ import annotations

import subprocess
from pathlib import Path

from tools.sandbox.sandbox_result import CommandResult


class SandboxError(RuntimeError):
    """Raised when a sandbox command cannot be started safely."""


class LocalSandbox:
    """Run commands inside an explicitly supplied workspace.

    This is a development primitive, not a security boundary. Production use must
    add OS/container isolation before executing untrusted projects.
    """

    def __init__(self, workspace: str | Path) -> None:
        self.workspace = Path(workspace).resolve()
        if not self.workspace.is_dir():
            raise SandboxError(f"Workspace does not exist: {self.workspace}")

    def run(self, command: str, *, timeout: float = 60.0) -> CommandResult:
        if not command.strip():
            raise ValueError("Command must not be empty")
        if timeout <= 0:
            raise ValueError("Timeout must be greater than zero")

        try:
            completed = subprocess.run(
                command,
                cwd=self.workspace,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or ""
            stderr = exc.stderr or ""
            if isinstance(stdout, bytes):
                stdout = stdout.decode(errors="replace")
            if isinstance(stderr, bytes):
                stderr = stderr.decode(errors="replace")
            return CommandResult(command, -1, stdout, stderr, timed_out=True)
        except OSError as exc:
            raise SandboxError(f"Unable to execute command: {exc}") from exc

        return CommandResult(
            command=command,
            return_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
