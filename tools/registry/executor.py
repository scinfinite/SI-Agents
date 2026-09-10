from __future__ import annotations

from collections.abc import Callable
from typing import Any

from core.policies.permission_engine import PermissionEngine
from tools.registry.registry import ToolRegistry, ToolStatus


class ToolExecutionError(RuntimeError):
    """Raised when a registered tool cannot be invoked safely."""


class ToolExecutor:
    """Bind registered tool descriptors to implementations and enforce their permissions."""

    def __init__(self, registry: ToolRegistry, *, permissions: PermissionEngine | None = None) -> None:
        self.registry = registry
        self.permissions = permissions or PermissionEngine()
        self._bindings: dict[str, object] = {}

    def bind(self, tool_id: str, implementation: object) -> None:
        descriptor = self.registry.get(tool_id)
        if descriptor.status in {ToolStatus.BLOCKED, ToolStatus.DEPRECATED}:
            raise ToolExecutionError(f"Tool is not executable: {descriptor.name}")
        if tool_id in self._bindings:
            raise ValueError(f"Tool already bound: {tool_id}")
        self._bindings[tool_id] = implementation

    def bind_name(self, name: str, implementation: object) -> None:
        matches = tuple(tool for tool in self.registry.all() if tool.name == name)
        if not matches:
            raise KeyError(f"Unknown tool: {name}")
        self.bind(matches[0].id, implementation)

    def invoke(
        self,
        tool_id: str,
        operation: str,
        *args: Any,
        agent: str | None = None,
        approval_granted: bool = False,
        **kwargs: Any,
    ) -> Any:
        descriptor = self.registry.get(tool_id)
        if descriptor.status in {ToolStatus.BLOCKED, ToolStatus.DEPRECATED}:
            raise ToolExecutionError(f"Tool is not executable: {descriptor.name}")
        implementation = self._bindings.get(tool_id)
        if implementation is None:
            raise ToolExecutionError(f"Tool is not bound: {descriptor.name}")
        if not operation or operation.startswith("_"):
            raise ValueError("Tool operation must be a public method name")
        method = getattr(implementation, operation, None)
        if not callable(method):
            raise ToolExecutionError(f"Unknown tool operation: {descriptor.name}.{operation}")
        for permission in descriptor.permissions:
            self.permissions.require(
                permission,
                approval_granted=approval_granted,
                agent=agent,
                tool=descriptor.name,
            )
        return method(*args, **kwargs)

    def bound(self, tool_id: str) -> bool:
        self.registry.get(tool_id)
        return tool_id in self._bindings

    def operation(self, tool_id: str, operation: str) -> Callable[..., Any]:
        descriptor = self.registry.get(tool_id)
        implementation = self._bindings.get(tool_id)
        if implementation is None:
            raise ToolExecutionError(f"Tool is not bound: {descriptor.name}")
        method = getattr(implementation, operation, None)
        if not callable(method):
            raise ToolExecutionError(f"Unknown tool operation: {descriptor.name}.{operation}")
        return method
