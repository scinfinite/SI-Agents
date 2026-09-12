"""Advanced, dependency-free SI operator control center."""
from __future__ import annotations

import json
import os
import shutil
import sys
from dataclasses import dataclass, replace
from typing import TextIO

from core.control_api.service import ControlApiService

# Historical views remain stable; each now supports advanced navigation/inspection.
VIEWS = (
    "overview", "agents", "teams", "workflows", "skills", "memory", "knowledge",
    "evidence", "runs", "organization", "governance", "environments", "harnesses", "settings",
)


@dataclass(frozen=True, slots=True)
class TuiState:
    view: str = "overview"
    filter_text: str = ""
    selected: int = 0
    detail: bool = False
    paused: bool = False
    sort_key: str = ""
    status_message: str = "ready"


class TuiApp:
    """Keyboard-first cockpit; SI Core remains the sole authority."""

    def __init__(self, service: ControlApiService, *, color: bool = True, page_size: int = 20) -> None:
        if not 1 <= page_size <= 100:
            raise ValueError("page_size must be between 1 and 100")
        self.service = service
        self.state = TuiState()
        self.color = color and sys.stdout.isatty() and not terminal_colors_disabled()
        self.page_size = page_size
        self.last_data: object = None
        self.approval_subject = ""
        self.approval_project = ""

    def _data(self) -> object:
        readers = {
            "overview": self.service.snapshot().as_dict,
            "agents": self.service.agents, "teams": self.service.teams,
            "workflows": self.service.workflows, "skills": self.service.skills,
            "memory": self.service.memory, "knowledge": lambda: {"status": "available through the core Knowledge service"},
            "evidence": self.service.evidence, "runs": self.service.runs,
            "organization": self.service.organization, "governance": self.service.governance_state,
            "environments": self.service.environments, "harnesses": self.service.harnesses,
            "settings": self.service.settings,
        }
        return readers[self.state.view]()

    def _filtered(self, data: object) -> object:
        needle = self.state.filter_text.casefold().strip()
        if isinstance(data, list):
            result = [item for item in data if not needle or needle in repr(item).casefold()]
            if self.state.sort_key:
                key = self.state.sort_key
                result.sort(key=lambda item: str(item.get(key, "")).casefold() if isinstance(item, dict) else str(item).casefold())
            return result
        if isinstance(data, dict) and needle:
            return {k: v for k, v in data.items() if needle in str(k).casefold() or needle in repr(v).casefold()}
        return data

    def refresh(self) -> object:
        if not self.state.paused:
            self.last_data = self._filtered(self._data())
            if isinstance(self.last_data, list):
                self.state = replace(self.state, selected=min(self.state.selected, max(0, len(self.last_data) - 1)))
        return self.last_data

    def render(self) -> str:
        data = self.refresh()
        width = max(60, shutil.get_terminal_size((100, 30)).columns)
        bar = "=" * min(width, 110)
        lines = [bar, f"SI-AGENTS TUI  |  {self.state.view.upper()}", bar]
        lines.append(f"state: {'PAUSED' if self.state.paused else 'LIVE'} | filter: {self.state.filter_text or '-'} | sort: {self.state.sort_key or '-'} | {self.state.status_message}")
        lines.append("views: " + "  ".join(f"{i + 1}:{name}" for i, name in enumerate(VIEWS)))
        lines.append("-" * min(width, 110))
        if isinstance(data, dict):
            for key, value in data.items():
                text = str(value).replace("\n", " ")
                lines.append(f"{key}: {text[:max(20, width - len(str(key)) - 2)]}")
        elif isinstance(data, list):
            lines.append(f"items: {len(data)} | selected: {self.state.selected + 1 if data else '-'}")
            if data and self.state.detail:
                item = data[self.state.selected]
                if isinstance(item, dict):
                    lines.extend(f"{k}: {str(v)[:max(20, width - len(str(k)) - 2)]}" for k, v in item.items())
                else:
                    lines.append(str(item)[:width])
            else:
                for index, item in enumerate(data[: self.page_size]):
                    marker = ">" if index == self.state.selected else " "
                    summary = json.dumps(item, ensure_ascii=False, sort_keys=True) if isinstance(item, dict) else str(item)
                    lines.append(f"{marker} {index + 1:03d} {summary[:max(20, width - 7)]}")
                if len(data) > self.page_size:
                    lines.append(f"... {len(data) - self.page_size} more; narrow with /text")
        else:
            lines.append(str(data))
        lines.extend(("", "[j/k] select  [n/p] view  [d/Enter] detail  [/] filter  [s field] sort", "[space] pause  [r] refresh  [?] help  [q] quit  [run ...] governed run  [approve ...] governed approval"))
        return "\n".join(lines)

    def help_text(self) -> str:
        return "\n".join((
            "SI-AGENTS ADVANCED TUI", "1-14: views | view <name>: direct navigation | j/k: selection | n/p: views",
            "/text: filter | s [field]: sort/clear | d or enter: detail | space/pause: pause refresh | r: refresh",
            "export: serialize snapshot into status | run <action> <subject> [risk]: governed run",
            "approve <id> <decision> <subject> <project> [reason]: identity-bound approval | q: quit",
        ))

    def _status(self, message: str) -> bool:
        self.state = replace(self.state, status_message=message)
        return True

    def _run_command(self, parts: list[str]) -> bool:
        if len(parts) < 3:
            return self._status("usage: run <action> <subject> [risk]")
        payload: dict[str, object] = {"action": parts[1], "subject": parts[2]}
        if len(parts) > 3:
            payload["risk"] = parts[3]
        try:
            result = self.service.create_run(payload)
            return self._status(f"run accepted: {result['id']}")
        except (ValueError, PermissionError, KeyError) as exc:
            return self._status(f"run rejected: {exc}")

    def _approval_command(self, parts: list[str]) -> bool:
        if len(parts) < 5:
            return self._status("usage: approve <id> <decision> <subject> <project> [reason]")
        payload: dict[str, object] = {"decision": parts[2], "subject_id": parts[3], "project_id": parts[4], "decision_by": parts[3], "reason": " ".join(parts[5:])}
        try:
            result = self.service.decide_approval(parts[1], payload)
            return self._status(f"approval {result['state']}: {parts[1]}")
        except (ValueError, PermissionError, KeyError) as exc:
            return self._status(f"approval rejected: {exc}")

    def handle(self, command: str) -> bool:
        command = command.strip()
        if not command:
            return True
        if command in {"q", "quit", "exit"}:
            return False
        if command in {"?", "help"}:
            return self._status("help available through app.help_text()")
        if command in {"r", "refresh"}:
            self.refresh(); return self._status("refreshed")
        if command in {"space", "pause"}:
            paused = not self.state.paused
            self.state = replace(self.state, paused=paused, status_message="paused" if paused else "live")
            return True
        if command in {"j", "down"}:
            data = self.refresh(); maximum = max(0, len(data) - 1) if isinstance(data, list) else 0
            self.state = replace(self.state, selected=min(maximum, self.state.selected + 1)); return True
        if command in {"k", "up"}:
            self.state = replace(self.state, selected=max(0, self.state.selected - 1)); return True
        if command in {"d", "detail", "enter"}:
            enabled = not self.state.detail; self.state = replace(self.state, detail=enabled, status_message=f"detail {'on' if enabled else 'off'}"); return True
        if command.startswith("/"):
            self.state = replace(self.state, filter_text=command[1:].strip(), selected=0, status_message="filter updated"); return True
        if command == "s":
            self.state = replace(self.state, sort_key="", status_message="sort cleared"); return True
        if command.startswith("s "):
            self.state = replace(self.state, sort_key=command[2:].strip(), selected=0, status_message="sort updated"); return True
        if command in {"n", "next"}:
            self.state = replace(self.state, view=VIEWS[(VIEWS.index(self.state.view) + 1) % len(VIEWS)], selected=0); return True
        if command in {"p", "prev"}:
            self.state = replace(self.state, view=VIEWS[(VIEWS.index(self.state.view) - 1) % len(VIEWS)], selected=0); return True
        if command.startswith("view "):
            name = command[5:].strip()
            if name in VIEWS: self.state = replace(self.state, view=name, selected=0)
            else: self._status(f"unknown view: {name}")
            return True
        if command.isdigit() and 1 <= int(command) <= len(VIEWS):
            self.state = replace(self.state, view=VIEWS[int(command) - 1], selected=0); return True
        if command == "export":
            return self._status(json.dumps(self.refresh(), ensure_ascii=False, sort_keys=True)[:240])
        parts = command.split()
        if parts and parts[0] == "run": return self._run_command(parts)
        if parts and parts[0] == "approve": return self._approval_command(parts)
        return self._status(f"unknown command: {parts[0]}")

    def run(self, *, stdin: TextIO | None = None, stdout: TextIO | None = None) -> int:
        stdin = stdin or sys.stdin; stdout = stdout or sys.stdout
        interactive = stdin.isatty() and stdout.isatty()
        while True:
            if interactive: stdout.write("\033[2J\033[H")
            stdout.write(self.render() + "\n"); stdout.flush()
            if not interactive: return 0
            command = stdin.readline()
            if not command or not self.handle(command): return 0


def terminal_colors_disabled() -> bool:
    return bool(os.environ.get("NO_COLOR"))
