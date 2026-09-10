from __future__ import annotations

from pathlib import Path

from tools.registry.contracts import ToolResult


class ContainerTool:
    """Adapter around an injected container executor; it never implements isolation itself."""

    def __init__(self, backend) -> None:
        self.backend = backend

    @property
    def workspace(self) -> str | Path:
        return self.backend.workspace

    def run(self, command: str, *, timeout: float = 60.0) -> ToolResult:
        try:
            result = self.backend.run(command, timeout=timeout)
        except (OSError, RuntimeError, ValueError) as exc:
            return ToolResult(False, error=str(exc))
        return ToolResult(result.succeeded, result.stdout, result.stderr)
