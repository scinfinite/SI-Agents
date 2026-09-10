from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class PermissionDecision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    APPROVAL_REQUIRED = "approval_required"


class PermissionDenied(PermissionError):
    """Raised when an action is denied by policy."""


@dataclass(frozen=True)
class PermissionScope:
    """Optional task/agent/tool scope layered on top of global policy."""

    agent: str | None = None
    tool: str | None = None
    capabilities: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True)
class PermissionEngine:
    """Evaluate action capabilities using deny-by-default semantics."""

    allow_read_filesystem: bool = True
    allow_read_repository: bool = True
    allow_read_documentation: bool = True
    allow_write_workspace: bool = True
    allow_write_repository: bool = False
    allow_local_commands: bool = True
    allow_destructive_commands: bool = False
    scopes: tuple[PermissionScope, ...] = ()

    def decide(
        self,
        capability: str,
        *,
        approval_granted: bool = False,
        agent: str | None = None,
        tool: str | None = None,
    ) -> PermissionDecision:
        normalized = capability.strip().lower()
        if not normalized:
            raise ValueError("Capability must not be empty")

        scope_matches = [scope for scope in self.scopes if self._scope_matches(scope, agent, tool)]
        if self.scopes and not scope_matches:
            return PermissionDecision.DENY
        if scope_matches and not any(normalized in scope.capabilities for scope in scope_matches):
            return PermissionDecision.DENY

        if normalized in {
            "destructive_git",
            "destructive_filesystem",
            "production_deploy",
            "credential_rotation",
            "publication",
            "paid_resource",
            "sensitive_data_transfer",
        }:
            return PermissionDecision.ALLOW if approval_granted else PermissionDecision.APPROVAL_REQUIRED

        allowed = {
            "filesystem_read": self.allow_read_filesystem,
            "repository_read": self.allow_read_repository,
            "documentation_read": self.allow_read_documentation,
            "workspace_write": self.allow_write_workspace,
            "repository_write": self.allow_write_repository,
            "local_command": self.allow_local_commands,
            "destructive_command": self.allow_destructive_commands,
        }.get(normalized)
        if allowed is None:
            return PermissionDecision.DENY
        return PermissionDecision.ALLOW if allowed else PermissionDecision.DENY

    def require(
        self,
        capability: str,
        *,
        approval_granted: bool = False,
        agent: str | None = None,
        tool: str | None = None,
    ) -> None:
        decision = self.decide(
            capability,
            approval_granted=approval_granted,
            agent=agent,
            tool=tool,
        )
        if decision is PermissionDecision.DENY:
            raise PermissionDenied(f"Capability denied by policy: {capability}")
        if decision is PermissionDecision.APPROVAL_REQUIRED:
            raise PermissionDenied(f"Approval required for capability: {capability}")

    @staticmethod
    def _scope_matches(scope: PermissionScope, agent: str | None, tool: str | None) -> bool:
        return (scope.agent is None or scope.agent == agent) and (scope.tool is None or scope.tool == tool)
