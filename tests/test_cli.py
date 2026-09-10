from __future__ import annotations

import json
from pathlib import Path

from core.cli.config import SIConfig, config_path, load_config, save_config
from core.cli.main import _opencode_install_plan, build_parser, cmd_agents, cmd_teams


def test_cli_parser_exposes_phase_27_commands() -> None:
    parser = build_parser()
    cases = {
        "doctor": ["doctor"],
        "status": ["status"],
        "agents": ["agents"],
        "teams": ["teams"],
        "setup": ["setup"],
        "update": ["update"],
        "run": ["run", "engineering-repair", "--objective", "x"],
    }
    for command, argv in cases.items():
        args = parser.parse_args(argv)
        assert args.command == command


def test_cli_parser_exposes_phase_28_handoff_commands() -> None:
    parser = build_parser()
    create = parser.parse_args(
        [
            "handoff", "create", "engineering-repair", "--objective", "x",
            "--source", "termux", "--target", "codespace", "--output", "handoff.json",
        ]
    )
    assert create.command == "handoff"
    assert create.handoff_command == "create"
    inspect = parser.parse_args(["handoff", "inspect", "handoff.json"])
    assert inspect.handoff_command == "inspect"
    import_args = parser.parse_args(["handoff", "import", "handoff.json"])
    assert import_args.handoff_command == "import"
    resumed = parser.parse_args(
        ["run", "engineering-repair", "--objective", "x", "--handoff", "handoff.json"]
    )
    assert resumed.handoff == "handoff.json"


def test_config_round_trip_uses_only_non_secret_fields(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    config = SIConfig(
        environment="termux",
        workspace="/tmp/project",
        opencode_url="http://127.0.0.1:4096",
        omniroute_url="http://127.0.0.1:20128",
        omniroute_model="example-model",
    )
    save_config(config, path)
    loaded = load_config(path)
    assert loaded == config
    assert json.loads(path.read_text(encoding="utf-8"))["omniroute_url"] == config.omniroute_url
    assert "api_key" not in path.read_text(encoding="utf-8").lower()
    assert path.stat().st_mode & 0o077 == 0


def test_config_path_honors_explicit_environment(monkeypatch, tmp_path: Path) -> None:
    target = tmp_path / "si.json"
    monkeypatch.setenv("SI_CONFIG", str(target))
    assert config_path() == target


def test_opencode_install_plan_uses_official_npm_package(monkeypatch) -> None:
    shutil_module = _opencode_install_plan.__globals__["shutil"]
    monkeypatch.setattr(shutil_module, "which", lambda name: "npm" if name == "npm" else None)
    assert _opencode_install_plan() == ("npm", "install", "-g", "opencode-ai")


def test_catalog_commands_use_canonical_sources(capsys) -> None:
    assert cmd_agents(type("Args", (), {})()) == 0
    assert cmd_teams(type("Args", (), {})()) == 0
    output = capsys.readouterr().out
    assert "engineering" in output.lower()
    assert "engineering-repair" in output
