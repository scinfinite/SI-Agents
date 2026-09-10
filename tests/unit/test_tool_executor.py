from __future__ import annotations

import pytest

from core.policies.permission_engine import PermissionEngine, PermissionScope
from tools.registry.executor import ToolExecutionError, ToolExecutor
from tools.registry.registry import ToolDescriptor, ToolRegistry, ToolStatus


class EchoTool:
    def echo(self, value: str) -> str:
        return value

    def _private(self) -> str:
        return "secret"


def test_executor_binds_and_enforces_descriptor_permissions() -> None:
    registry = ToolRegistry()
    descriptor = registry.register(
        ToolDescriptor("echo", "test", permissions=("web_read",), verification=("echo test",))
    )
    executor = ToolExecutor(registry)
    executor.bind(descriptor.id, EchoTool())
    assert executor.bound(descriptor.id)
    assert executor.invoke(descriptor.id, "echo", "hello") == "hello"


def test_executor_denies_unmatched_scoped_tool() -> None:
    registry = ToolRegistry()
    descriptor = registry.register(ToolDescriptor("echo", "test", permissions=("web_read",)))
    permissions = PermissionEngine(
        scopes=(PermissionScope(agent="researcher", tool="other", capabilities=frozenset({"web_read"})),)
    )
    executor = ToolExecutor(registry, permissions=permissions)
    executor.bind(descriptor.id, EchoTool())
    with pytest.raises(PermissionError):
        executor.invoke(descriptor.id, "echo", "blocked", agent="researcher")


def test_executor_rejects_blocked_and_private_operations() -> None:
    registry = ToolRegistry()
    blocked = registry.register(ToolDescriptor("blocked", "test", status=ToolStatus.BLOCKED))
    executor = ToolExecutor(registry)
    with pytest.raises(ToolExecutionError):
        executor.bind(blocked.id, EchoTool())

    descriptor = registry.register(ToolDescriptor("echo", "test"))
    executor.bind(descriptor.id, EchoTool())
    with pytest.raises(ValueError):
        executor.invoke(descriptor.id, "_private")
