from __future__ import annotations

import subprocess
from pathlib import Path

from tools.sandbox.command_policy import CommandPolicy
from tools.sandbox.sandbox_result import CommandResult


class SandboxError(RuntimeError):
    """Raised when a local command cannot be started safely."""


class LocalSandbox:
    """Run approved commands inside an explicitly supplied workspace.

    This is a development executor, not a security boundary. Production use must
    add OS/container isolation before executing untrusted projects.
    """

    def __init__(
        self,
        workspace: str | Path,
        *,
        policy: CommandPolicy | None = None,
    ) -> None:
        self.workspace = Path(workspace).resolve()
        if not self.workspace.is_dir():
            raise SandboxError(f"Workspace does not exist: {self.workspace}")
        self.policy = policy or CommandPolicy()

    def run(self, command: str, *, timeout: float = 60.0) -> CommandResult:
        self.policy.check(command)
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
