from __future__ import annotations

import importlib
import json
from pathlib import Path

from core.cli.audit import audit_summary
from core.cli.main import build_parser, cmd_agents, cmd_personas, cmd_status, cmd_teams


def test_audit_passes_on_repository() -> None:
    result = audit_summary(Path(__file__).resolve().parents[1])
    assert result["ok"] is True, result


def test_parser_exposes_audit_personas_and_filters() -> None:
    parser = build_parser()
    assert parser.parse_args(["audit"]).command == "audit"
    personas = parser.parse_args(["personas", "--division", "si-engineering", "--json"])
    assert personas.command == "personas"
    assert personas.division == "si-engineering"
    agents = parser.parse_args(["agents", "--search", "engineer", "--json"])
    assert agents.search == "engineer"
    teams = parser.parse_args(["teams", "--search", "repair", "--json"])
    assert teams.search == "repair"


def test_enhanced_catalog_commands_support_json(capsys) -> None:
    assert cmd_agents(type("Args", (), {"division": "si-engineering", "status": None, "search": None, "json": True})()) == 0
    agents = json.loads(capsys.readouterr().out)
    assert agents
    assert all(item["division"] == "si-engineering" for item in agents)

    assert cmd_personas(type("Args", (), {"division": "si-engineering", "search": "engineer", "json": True})()) == 0
    personas = json.loads(capsys.readouterr().out)
    assert personas
    assert all("engineer" in item["name"].casefold() or "engineer" in item["id"] for item in personas)

    assert cmd_teams(type("Args", (), {"search": "repair", "json": True})()) == 0
    teams = json.loads(capsys.readouterr().out)
    assert teams
    assert all("repair" in (item["id"] + item["name"] + item["description"]).casefold() for item in teams)


def test_status_json_is_structured(monkeypatch, capsys, tmp_path: Path) -> None:
    cli = importlib.import_module("core.cli.main")

    monkeypatch.setenv("SI_CONFIG", str(tmp_path / "config.json"))
    monkeypatch.setattr(cli, "_report", lambda: type(
        "Report", (), {
            "kind": type("Kind", (), {"value": "test"})(),
            "status": type("Status", (), {"value": "ready"})(),
        }
    )())
    monkeypatch.setattr(cli, "_exit_code", lambda status: 0)
    args = type("Args", (), {"json": True})()
    assert cmd_status(args) == 0
    payload = json.loads(capsys.readouterr().out)
    assert "version" in payload
    assert payload["environment"] == "test"
