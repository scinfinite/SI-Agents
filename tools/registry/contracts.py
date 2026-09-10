from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class ToolResult:
    """Common result envelope for tools that perform read or transformation work."""

    succeeded: bool
    value: str = ""
    error: str = ""


class FileSystemTool(Protocol):
    def read_text(self, path: str | Path) -> str: ...
    def write_text(self, path: str | Path, content: str) -> None: ...
    def list(self, path: str | Path = ".") -> tuple[str, ...]: ...
    def exists(self, path: str | Path) -> bool: ...


class SourceControlTool(Protocol):
    def run(self, args: tuple[str, ...]) -> ToolResult: ...


class WebTool(Protocol):
    def fetch(self, url: str, *, timeout: float = 15.0) -> ToolResult: ...
