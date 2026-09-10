from __future__ import annotations

from typing import Protocol

from tools.sandbox.sandbox_result import CommandResult


class ExecutionBackend(Protocol):
    """Backend contract for policy-approved command execution."""

    @property
    def workspace(self) -> str:
        """Return the canonical workspace used by this backend."""

    def run(self, command: str, *, timeout: float = 60.0) -> CommandResult:
        """Execute a command and return its raw result."""
