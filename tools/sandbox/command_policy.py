from __future__ import annotations

from dataclasses import dataclass


class CommandPolicyError(PermissionError):
    """Raised when a command violates the local execution policy."""


@dataclass(frozen=True)
class CommandPolicy:
    """Minimal policy gate for local command execution.

    This is intentionally conservative and is not a security boundary. It prevents
    obviously destructive commands from being executed by the development executor.
    A production sandbox must enforce isolation at the OS/container boundary.
    """

    destructive_prefixes: tuple[str, ...] = (
        "rm -rf /",
        "rm -rf /*",
        "mkfs",
        "shutdown",
        "reboot",
        "poweroff",
    )

    def check(self, command: str) -> None:
        normalized = command.strip().lower()
        if not normalized:
            raise ValueError("Command must not be empty")
        if any(normalized.startswith(prefix) for prefix in self.destructive_prefixes):
            raise CommandPolicyError("Command blocked by local execution policy")
