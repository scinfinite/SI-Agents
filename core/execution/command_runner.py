from __future__ import annotations

from core.execution.execution_backend import ExecutionBackend
from core.execution.execution_record import ExecutionRecord
from core.policies.permission_engine import PermissionDecision, PermissionEngine
from tools.sandbox.sandbox_result import CommandResult


class CommandRunner:
    """Task-aware command execution with permission and backend policy gates."""

    def __init__(
        self,
        backend: ExecutionBackend,
        *,
        permissions: PermissionEngine | None = None,
    ) -> None:
        self.backend = backend
        self.permissions = permissions or PermissionEngine()

    def run(self, task_id: str, command: str, *, timeout: float = 60.0) -> ExecutionRecord:
        self.permissions.require("local_command")
        result: CommandResult = self.backend.run(command, timeout=timeout)
        return ExecutionRecord(
            task_id=task_id,
            command=result.command,
            workspace=str(self.backend.workspace),
            return_code=result.return_code,
            stdout=result.stdout,
            stderr=result.stderr,
            timed_out=result.timed_out,
            policy_decision=PermissionDecision.ALLOW.value,
            started_at=result.started_at,
        )
