from __future__ import annotations

import ast
from pathlib import Path

from tools.registry.contracts import ToolResult


class PythonParserTool:
    """AST parser for Python source inside a workspace."""

    def __init__(self, workspace: str | Path) -> None:
        self.workspace = Path(workspace).resolve()
        if not self.workspace.is_dir():
            raise ValueError(f"Workspace does not exist: {self.workspace}")

    def parse(self, path: str | Path) -> ToolResult:
        target = (self.workspace / path).resolve()
        try:
            target.relative_to(self.workspace)
            tree = ast.parse(target.read_text(encoding="utf-8"), filename=str(target))
        except (OSError, UnicodeDecodeError, SyntaxError, ValueError) as exc:
            return ToolResult(False, error=str(exc))
        return ToolResult(True, value=ast.dump(tree, indent=2))
