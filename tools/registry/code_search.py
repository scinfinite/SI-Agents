from __future__ import annotations

import re
from pathlib import Path

from tools.registry.contracts import ToolResult


class CodeSearchTool:
    """Simple deterministic source search that stays inside a workspace."""

    def __init__(self, workspace: str | Path) -> None:
        self.workspace = Path(workspace).resolve()
        if not self.workspace.is_dir():
            raise ValueError(f"Workspace does not exist: {self.workspace}")

    def search(self, pattern: str, *, suffixes: tuple[str, ...] = ()) -> ToolResult:
        if not pattern:
            raise ValueError("Search pattern must not be empty")
        regex = re.compile(pattern)
        matches: list[str] = []
        for path in self.workspace.rglob("*"):
            if not path.is_file() or (suffixes and path.suffix not in suffixes):
                continue
            try:
                for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                    if regex.search(line):
                        matches.append(f"{path.relative_to(self.workspace)}:{number}:{line}")
            except (OSError, UnicodeDecodeError):
                continue
        return ToolResult(True, value="\n".join(matches))
