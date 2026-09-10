from __future__ import annotations

from pathlib import Path

from tools.registry.contracts import ToolResult


class FileSystemToolImpl:
    """Workspace-scoped filesystem operations with traversal protection."""

    def __init__(self, workspace: str | Path) -> None:
        self.workspace = Path(workspace).resolve()
        if not self.workspace.is_dir():
            raise ValueError(f"Workspace does not exist: {self.workspace}")

    def _resolve(self, path: str | Path) -> Path:
        candidate = (self.workspace / path).resolve()
        try:
            candidate.relative_to(self.workspace)
        except ValueError as exc:
            raise PermissionError("Path escapes workspace") from exc
        return candidate

    def read_text(self, path: str | Path) -> str:
        return self._resolve(path).read_text(encoding="utf-8")

    def write_text(self, path: str | Path, content: str) -> None:
        target = self._resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def list(self, path: str | Path = ".") -> tuple[str, ...]:
        return tuple(sorted(item.name for item in self._resolve(path).iterdir()))

    def exists(self, path: str | Path) -> bool:
        return self._resolve(path).exists()

    def read_result(self, path: str | Path) -> ToolResult:
        try:
            return ToolResult(True, value=self.read_text(path))
        except (OSError, PermissionError) as exc:
            return ToolResult(False, error=str(exc))
