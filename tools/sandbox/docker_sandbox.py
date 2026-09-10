from __future__ import annotations

import subprocess
from pathlib import Path

from tools.sandbox.sandbox_result import CommandResult


class DockerSandboxError(RuntimeError):
    """Raised when the Docker-backed executor cannot be used safely."""


class DockerSandbox:
    """Execute commands in a Docker container with a conservative baseline.

    The Docker daemon remains a privileged trust boundary. This backend is intended
    for untrusted project code only when the daemon itself is trusted and isolated.
    """

    def __init__(
        self,
        workspace: str | Path,
        *,
        image: str = "python:3.11-slim",
        memory: str = "512m",
        cpus: str = "1.0",
        pids_limit: int = 256,
    ) -> None:
        self.workspace = Path(workspace).resolve()
        if not self.workspace.is_dir():
            raise DockerSandboxError(f"Workspace does not exist: {self.workspace}")
        if not image.strip():
            raise ValueError("Docker image must not be empty")
        if pids_limit <= 0:
            raise ValueError("PID limit must be greater than zero")
        self.image = image.strip()
        self.memory = memory
        self.cpus = cpus
        self.pids_limit = pids_limit

    def _argv(self, command: str) -> list[str]:
        if not command.strip():
            raise ValueError("Command must not be empty")
        return [
            "docker",
            "run",
            "--rm",
            "--network=none",
            "--read-only",
            "--cap-drop=ALL",
            "--security-opt=no-new-privileges",
            f"--memory={self.memory}",
            f"--cpus={self.cpus}",
            f"--pids-limit={self.pids_limit}",
            "--tmpfs=/tmp:rw,noexec,nosuid,size=64m",
            f"--mount=type=bind,src={self.workspace},dst=/workspace,rw",
            "--workdir=/workspace",
            self.image,
            "/bin/sh",
            "-lc",
            command,
        ]

    def run(self, command: str, *, timeout: float = 60.0) -> CommandResult:
        if timeout <= 0:
            raise ValueError("Timeout must be greater than zero")
        argv = self._argv(command)
        try:
            completed = subprocess.run(
                argv,
                cwd=self.workspace,
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
            raise DockerSandboxError(f"Unable to start Docker: {exc}") from exc

        return CommandResult(
            command=command,
            return_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
