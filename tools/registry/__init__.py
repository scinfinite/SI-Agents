from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol
from uuid import uuid4


class ToolStatus(str, Enum):
    UNKNOWN = "unknown"
    EXPERIMENTAL = "experimental"
    VALIDATED = "validated"
    DEPRECATED = "deprecated"
    BLOCKED = "blocked"


class Tool(Protocol):
    name: str
    category: str
    status: ToolStatus
    permissions: tuple[str, ...]

    def available(self) -> bool: ...


@dataclass(frozen=True)
class ToolDescriptor:
    name: str
    category: str
    status: ToolStatus = ToolStatus.UNKNOWN
    description: str = ""
    permissions: tuple[str, ...] = ()
    inputs: tuple[str, ...] = ()
    outputs: tuple[str, ...] = ()
    verification: tuple[str, ...] = ()
    version: str = "1"
    id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Tool name must not be empty")
        if not self.category.strip():
            raise ValueError("Tool category must not be empty")
        if self.status is ToolStatus.VALIDATED and not self.verification:
            raise ValueError("Validated tools must declare verification criteria")


class ToolRegistry:
    """Registry of executable tool descriptors; registration does not grant permission."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolDescriptor] = {}

    def register(self, tool: ToolDescriptor) -> ToolDescriptor:
        if tool.id in self._tools:
            raise ValueError(f"Duplicate tool id: {tool.id}")
        if any(existing.name == tool.name for existing in self._tools.values()):
            raise ValueError(f"Duplicate tool name: {tool.name}")
        self._tools[tool.id] = tool
        return tool

    def get(self, tool_id: str) -> ToolDescriptor:
        try:
            return self._tools[tool_id]
        except KeyError as exc:
            raise KeyError(f"Unknown tool: {tool_id}") from exc

    def all(self) -> tuple[ToolDescriptor, ...]:
        return tuple(self._tools.values())

    def by_category(self, category: str) -> tuple[ToolDescriptor, ...]:
        return tuple(tool for tool in self._tools.values() if tool.category == category)

    def by_status(self, status: ToolStatus) -> tuple[ToolDescriptor, ...]:
        return tuple(tool for tool in self._tools.values() if tool.status is status)
