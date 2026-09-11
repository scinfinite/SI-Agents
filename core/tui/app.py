"""Keyboard-first, dependency-free SI operator console.

The TUI reads the same ControlApiService used by the Web surface. It owns no
agent, workflow, governance, or execution authority.
"""

from __future__ import annotations

import os
import shutil
import sys
from dataclasses import dataclass
from typing import TextIO

from core.control_api.service import ControlApiService


@dataclass(frozen=True, slots=True)
class TuiState:
    view: str = "overview"
    filter_text: str = ""
    selected: int = 0


VIEWS = (
    "overview", "agents", "teams", "workflows", "skills", "memory", "knowledge",
    "evidence", "runs", "organization", "governance", "environments", "harnesses", "settings",
)


class TuiApp:
    """Small deterministic terminal UI; mutation is intentionally absent."""

    def __init__(self, service: ControlApiService, *, color: bool = True) -> None:
        self.service = service
        self.state = TuiState()
        self.color = color and sys.stdout.isatty()

    def _data(self) -> object:
        view = self.state.view
        readers = {
            "overview": self.service.snapshot().as_dict,
            "agents": self.service.agents,
            "teams": self.service.teams,
            "workflows": self.service.workflows,
            "skills": self.service.skills,
            "memory": self.service.memory,
            "knowledge": lambda: {"status": "available through the core Knowledge service"},
            "evidence": self.service.evidence,
            "runs": self.service.runs,
            "organization": self.service.organization,
            "governance": self.service.governance_state,
            "environments": self.service.environments,
            "harnesses": self.service.harnesses,
            "settings": self.service.settings,
        }
        return readers[view]()

    def _filtered(self, data: object) -> object:
        needle = self.state.filter_text.casefold().strip()
        if not needle or not isinstance(data, list):
            return data
        return [item for item in data if needle in repr(item).casefold()]

    def render(self) -> str:
        data = self._filtered(self._data())
        width = max(60, shutil.get_terminal_size((100, 24)).columns)
        title = f"SI-AGENTS TUI  |  {self.state.view.upper()}"
        lines = ["=" * min(width, 100), title, "=" * min(width, 100)]
        if self.state.filter_text:
            lines.append(f"filter: {self.state.filter_text}")
        if isinstance(data, dict):
            for key, value in data.items():
                text = str(value).replace("\n", " ")
                lines.append(f"{key}: {text[: max(20, width - len(key) - 2)]}")
        elif isinstance(data, list):
            lines.append(f"items: {len(data)}")
            for index, item in enumerate(data[:20]):
                marker = ">" if index == self.state.selected else " "
                lines.append(f"{marker} {index + 1:02d} {str(item)[: width - 7]}")
            if len(data) > 20:
                lines.append(f"... {len(data) - 20} more")
        else:
            lines.append(str(data))
        lines.extend(("", "[1-9] views  [n/p] view  [j/k] select  [/text] filter  [r] refresh  [q] quit"))
        return "\n".join(lines)

    def handle(self, command: str) -> bool:
        """Apply a local navigation command. Returns False only for quit."""
        command = command.strip()
        if command in {"q", "quit", "exit"}:
            return False
        if command in {"r", "refresh"}:
            return True
        if command in {"j", "down"}:
            self.state = TuiState(self.state.view, self.state.filter_text, self.state.selected + 1)
            return True
        if command in {"k", "up"}:
            self.state = TuiState(self.state.view, self.state.filter_text, max(0, self.state.selected - 1))
            return True
        if command.startswith("/"):
            self.state = TuiState(self.state.view, command[1:].strip(), 0)
            return True
        if command in {"n", "next"}:
            index = (VIEWS.index(self.state.view) + 1) % len(VIEWS)
            self.state = TuiState(VIEWS[index], self.state.filter_text, 0)
            return True
        if command in {"p", "prev"}:
            index = (VIEWS.index(self.state.view) - 1) % len(VIEWS)
            self.state = TuiState(VIEWS[index], self.state.filter_text, 0)
            return True
        if command.isdigit() and 1 <= int(command) <= len(VIEWS):
            self.state = TuiState(VIEWS[int(command) - 1], self.state.filter_text, 0)
            return True
        return True

    def run(self, *, stdin: TextIO | None = None, stdout: TextIO | None = None) -> int:
        stdin = stdin or sys.stdin
        stdout = stdout or sys.stdout
        interactive = stdin.isatty() and stdout.isatty()
        while True:
            if interactive:
                stdout.write("\033[2J\033[H")
            stdout.write(self.render() + "\n")
            stdout.flush()
            if not interactive:
                return 0
            command = stdin.readline()
            if not command or not self.handle(command):
                return 0


def terminal_colors_disabled() -> bool:
    return bool(os.environ.get("NO_COLOR"))
