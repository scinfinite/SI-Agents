from __future__ import annotations

from tools.sandbox.command_policy import CommandPolicy
from tools.sandbox.local_sandbox import LocalSandbox
from tools.sandbox.sandbox_result import CommandResult
from core.execution.execution_record import ExecutionRecord
from core.policies.permission_engine import PermissionEngine, PermissionDecision


class CommandRunner:
    """Task-aware command execution with permission and command-policy gates."""

    def __init__(self, sandbox: LocalSandbox, *, permissions: PermissionEngine | None = None) -> None:
        self.sandbox = sandbox
        self.permissions = permissions or PermissionEngine()

    def run(self, task_id: str, command: str, *, timeout: float = 60.0) -> ExecutionRecord:
        self.permissions.require("local_command")
        result: CommandResult
        try:
            result = self.sandbox.run(command, timeout=timeout)
        except Exception:
            raise
        return ExecutionRecord(
            task_id=task_id,
            command=result.command,
            workspace=str(self.sandbox.workspace),
            return_code=result.return_code,
            stdout=result.stdout,
            stderr=result.stderr,
            timed_out=result.timed_out,
            policy_decision=PermissionDecision.ALLOW.value,
            started_at=result.started_at,
        )
