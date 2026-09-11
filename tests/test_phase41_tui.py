"""Phase 41 TUI regression and adversarial coverage."""

from __future__ import annotations

from io import StringIO
from pathlib import Path

from core.control_api.service import ControlApiService
from core.tui.app import VIEWS, TuiApp, TuiState
from core.tui.cli import main


def service(tmp_path: Path) -> ControlApiService:
    return ControlApiService(Path(__file__).resolve().parents[1])


def test_views_are_deterministic_and_complete(tmp_path: Path) -> None:
    app = TuiApp(service(tmp_path), color=False)
    assert app.state.view == "overview"
    assert len(VIEWS) == 14
    assert "agents" in VIEWS
    assert "evidence" in VIEWS
    assert "governance" in VIEWS
    rendered = app.render()
    assert "SI-AGENTS TUI  |  OVERVIEW" in rendered
    assert "[1-9] views" in rendered


def test_navigation_filter_and_selection_are_local_only(tmp_path: Path) -> None:
    app = TuiApp(service(tmp_path), color=False)
    before_runs = app.service.runs()
    assert app.handle("2")
    assert app.state == TuiState("agents", "", 0)
    assert app.handle("/finance")
    assert app.state.filter_text == "finance"
    assert app.handle("j")
    assert app.state.selected == 1
    assert app.handle("k")
    assert app.state.selected == 0
    assert app.handle("p")
    assert app.state.view == "overview"
    assert app.service.runs() == before_runs


def test_unknown_commands_do_not_mutate_authoritative_state(tmp_path: Path) -> None:
    app = TuiApp(service(tmp_path), color=False)
    before = app.state
    assert app.handle("POST /api/v1/runs")
    assert app.state == before
    assert app.service.runs() == []


def test_quit_is_explicit(tmp_path: Path) -> None:
    app = TuiApp(service(tmp_path), color=False)
    assert not app.handle("q")


def test_noninteractive_run_renders_once(tmp_path: Path) -> None:
    app = TuiApp(service(tmp_path), color=False)
    output = StringIO()
    output.isatty = lambda: False  # type: ignore[method-assign]
    stdin = StringIO()
    assert app.run(stdin=stdin, stdout=output) == 0
    assert "SI-AGENTS TUI" in output.getvalue()


def test_cli_once_supports_view_and_filter(tmp_path: Path, capsys) -> None:
    assert main(["--root", str(Path(__file__).resolve().parents[1]), "--view", "evidence", "--filter", "run", "--once", "--no-color"]) == 0
    assert "EVIDENCE" in capsys.readouterr().out
