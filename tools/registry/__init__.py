from __future__ import annotations

from typing import Protocol

from tools.registry.registry import ToolDescriptor, ToolRegistry, ToolStatus


class Tool(Protocol):
    name: str
    category: str
    status: ToolStatus
    permissions: tuple[str, ...]

    def available(self) -> bool: ...


__all__ = ["Tool", "ToolDescriptor", "ToolRegistry", "ToolStatus"]
