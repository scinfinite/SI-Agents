"""Advanced, dependency-free SI operator control center.

The TUI is deliberately a thin client over :class:`ControlApiService`. It owns
no execution, workflow, persistence, authentication, or governance authority.
All mutations are routed through the existing governed service methods.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import time
from dataclasses import dataclass, replace
from typing import TextIO

from core.control_api.service import ControlApiService


VIEWS = (
    "overview", "runs", "events", "agents", "teams", "workflows", "topology",
    "approvals", "evidence", "governance", "environments", "harnesses", "skills",
    "memory", "knowledge", "organization", "settings",
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
    """Deterministic operator cockpit with bounded navigation and safe controls."""

    def __init__(self, service: ControlApiService, *, color: bool = True, page_size: int = 20) -> None:
        if page_size < 1 or page_size > 100:
            raise ValueError("page_size must be between 1 and 100")
        self.service = service
        self.state = TuiState()
        self.color = color and sys.stdout.isatty() and not terminal_colors_disabled()
        self.page_size = page_size
        self.last_data: object = None

    def _data(self) -> object:
        readers = {
            "overview": self.service.snapshot().as_dict,
            "runs": self.service.runs,
            "events": self.service.events,
            "agents": self.service.agents,
            "teams": self.service.teams,
            "workflows": self.service.workflows,
            "topology": self.service.visualization,
            "approvals": lambda: self.service.approvals_queue(
                subject_id=getattr(self, "approval_subject", ""),
                project_id=getattr(self, "approval_project", ""),
            ),
            "evidence": self.service.evidence,
            "governance": self.service.governance_state,
            "environments": self.service.environments,
            "harnesses": self.service.harnesses,
            "skills": self.service.skills,
            "memory": self.service.memory,
            "knowledge": lambda: {"status": "available through the core Knowledge service"},
            "organization": self.service.organization,
            "settings": self.service.settings,
        }
        return readers[self.state.view]()

    @staticmethod
    def _matches(item: object, needle: str) -> bool:
        return needle in repr(item).casefold()

    def _filtered(self, data: object) -> object:
        needle = self.state.filter_text.casefold().strip()
        if isinstance(data, list):
            values = [x for x in data if not needle or self._matches(x, needle)]
            if self.state.sort_key:
                key = self.state.sort_key
                values.sort(key=lambda x: str(x.get(key, "")).casefold() if isinstance(x, dict) else str(x).casefold())
            return values
        if isinstance(data, dict) and needle:
            return {k: v for k, v in data.items() if needle in str(k).casefold() or self._matches(v, needle)}
        return data

    def refresh(self) -> object:
        if not self.state.paused:
            self.last_data = self._filtered(self._data())
            if isinstance(self.last_data, list):
                maximum = max(0, len(self.last_data) - 1)
                if self.state.selected > maximum:
                    self.state = replace(self.state, selected=maximum)
        return self.last_data

    def _detail_text(self, item: object, width: int) -> list[str]:
        if isinstance(item, dict):
            return [f"{key}: {str(value).replace(chr(10), ' ')[:max(20, width - len(str(key)) - 2)]}" for key, value in item.items()]
        return [str(item)[:width]]

    def render(self) -> str:
        data = self.refresh()
        width = max(60, shutil.get_terminal_size((100, 30)).columns)
        bar = "=" * min(width, 110)
        lines = [bar, f"SI-AGENTS CONTROL CENTER  |  {self.state.view.upper()}", bar]
        lines.append(f"state: {'PAUSED' if self.state.paused else 'LIVE'} | filter: {self.state.filter_text or '-'} | sort: {self.state.sort_key or '-'} | {self.state.status_message}")
        lines.append("views: " + "  ".join(f"{i + 1}:{name}" for i, name in enumerate(VIEWS[:9])))
        lines.append("       " + "  ".join(f"{i + 10}:{name}" for i, name in enumerate(VIEWS[9:])))
        lines.append("-" * min(width, 110))
        if isinstance(data, dict):
            for key, value in data.items():
                text = str(value).replace("\n", " ")
                lines.append(f"{key}: {text[:max(20, width - len(str(key)) - 2)]}")
        elif isinstance(data, list):
            lines.append(f"items: {len(data)} | selected: {self.state.selected + 1 if data else '-'}")
            if data and self.state.detail:
                lines.extend(self._detail_text(data[self.state.selected], width))
            else:
                for index, item in enumerate(data[: self.page_size]):
                    marker = ">" if index == self.state.selected else " "
                    summary = json.dumps(item, ensure_ascii=False, sort_keys=True) if isinstance(item, dict) else str(item)
                    lines.append(f"{marker} {index + 1:03d} {summary[:max(20, width - 7)]}")
                if len(data) > self.page_size:
                    lines.append(f"... {len(data) - self.page_size} more (use /filter to narrow)")
        else:
            lines.append(str(data))
        lines.extend(("", "[j/k] select  [n/p] next/prev view  [Enter/d] detail  [/] filter  [s] sort  [space] pause", "[r] refresh  [?] help  [q] quit  [run ...] governed run  [approve ...] governed approval"))
        return "\n".join(lines)

    def help_text(self) -> str:
        return "\n".join((
            "SI-AGENTS TUI COMMANDS",
            "  1-9 / 0: select numbered view (10+ via 'view <name>')",
            "  view <name>: select any view", "  j/k or up/down: move selection", "  n/p: next/previous view",
            "  /text: filter current list", "  s [field]: sort list by field; s clears sort",
            "  d / enter: toggle selected-item detail", "  space/pause: pause live refresh", "  r/refresh: refresh now",
            "  export: print current data as JSON", "  run <action> <subject> [risk]: governed run request",
            "  approve <id> <decision> <subject> <project> [reason]: identity-bound approval decision",
            "  q/quit/exit: leave the console",
        ))

    def _set_status(self, message: str) -> bool:
        self.state = replace(self.state, status_message=message)
        return True

    def _run_command(self, parts: list[str]) -> bool:
        if len(parts) < 3:
            return self._set_status("usage: run <action> <subject> [risk]")
        payload: dict[str, object] = {"action": parts[1], "subject": parts[2]}
        if len(parts) > 3:
            payload["risk"] = parts[3]
        try:
            result = self.service.create_run(payload)
            return self._set_status(f"run accepted: {result['id']}")
        except (ValueError, PermissionError, KeyError) as exc:
            return self._set_status(f"run rejected: {exc}")

    def _approval_command(self, parts: list[str]) -> bool:
        if len(parts) < 5:
            return self._set_status("usage: approve <id> <decision> <subject> <project> [reason]")
        payload: dict[str, object] = {"decision": parts[2], "subject_id": parts[3], "project_id": parts[4], "decision_by": parts[3], "reason": " ".join(parts[5:])}
        try:
            result = self.service.decide_approval(parts[1], payload)
            return self._set_status(f"approval {result['state']}: {parts[1]}")
        except (ValueError, PermissionError, KeyError) as exc:
            return self._set_status(f"approval rejected: {exc}")

    def handle(self, command: str) -> bool:
        """Apply a command. Unknown commands are harmless and reported in status."""
        command = command.strip()
        if not command:
            return True
        if command in {"q", "quit", "exit"}:
            return False
        if command in {"?", "help"}:
            return self._set_status("help: use '?' in the interactive console; see CLI --help for options")
        if command in {"r", "refresh"}:
            self.state = replace(self.state, status_message="refreshed")
            self.refresh()
            return True
        if command in {"space", "pause"}:
            self.state = replace(self.state, paused=not self.state.paused, status_message="paused" if not self.state.paused else "live")
            return True
        if command in {"j", "down"}:
            data = self.refresh()
            maximum = max(0, len(data) - 1) if isinstance(data, list) else 0
            self.state = replace(self.state, selected=min(maximum, self.state.selected + 1))
            return True
        if command in {"k", "up"}:
            self.state = replace(self.state, selected=max(0, self.state.selected - 1))
            return True
        if command in {"d", "detail", "enter"}:
            return self._set_status("detail " + ("on" if not self.state.detail else "off")) if not self._toggle_detail() else True
        if command.startswith("/"):
            self.state = replace(self.state, filter_text=command[1:].strip(), selected=0, status_message="filter updated")
            return True
        if command == "s":
            self.state = replace(self.state, sort_key="", status_message="sort cleared")
            return True
        if command.startswith("s "):
            self.state = replace(self.state, sort_key=command[2:].strip(), selected=0, status_message="sort updated")
            return True
        if command in {"n", "next"}:
            index = (VIEWS.index(self.state.view) + 1) % len(VIEWS)
            self.state = replace(self.state, view=VIEWS[index], selected=0)
            return True
        if command in {"p", "prev"}:
            index = (VIEWS.index(self.state.view) - 1) % len(VIEWS)
            self.state = replace(self.state, view=VIEWS[index], selected=0)
            return True
        if command.startswith("view "):
            name = command[5:].strip()
            if name in VIEWS:
                self.state = replace(self.state, view=name, selected=0, status_message=f"view: {name}")
            else:
                self._set_status(f"unknown view: {name}")
            return True
        if command.isdigit() and 1 <= int(command) <= len(VIEWS):
            self.state = replace(self.state, view=VIEWS[int(command) - 1], selected=0)
            return True
        if command == "export":
            self._set_status(json.dumps(self.refresh(), ensure_ascii=False)[:240])
            return True
        parts = command.split()
        if parts and parts[0] == "run":
            return self._run_command(parts)
        if parts and parts[0] == "approve":
            return self._approval_command(parts)
        return self._set_status(f"unknown command: {command.split()[0]}")

    def _toggle_detail(self) -> bool:
        self.state = replace(self.state, detail=not self.state.detail, status_message="detail on" if self.state.detail else "detail off")
        return True

    def run(self, *, stdin: TextIO | None = None, stdout: TextIO | None = None, refresh_seconds: float = 0.0) -> int:
        stdin = stdin or sys.stdin
        stdout = stdout or sys.stdout
        if refresh_seconds < 0 or refresh_seconds > 60:
            raise ValueError("refresh_seconds must be between 0 and 60")
        interactive = stdin.isatty() and stdout.isatty()
        while True:
            if interactive:
                stdout.write("\033[2J\033[H")
            stdout.write(self.render() + "\n")
            stdout.flush()
            if not interactive:
                return 0
            if refresh_seconds:
                # A timed refresh is intentionally bounded and never replaces input handling.
                time.sleep(refresh_seconds)
                continue
            command = stdin.readline()
            if not command or not self.handle(command):
                return 0


def terminal_colors_disabled() -> bool:
    return bool(os.environ.get("NO_COLOR"))
