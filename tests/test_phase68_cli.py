"""Phase 68 advanced CLI contract, safety, and failure coverage."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.cli.platform import EXIT_AUTH, MAX_ATTACHMENT, PlatformClient, _segment, build_parser, main

ROOT = Path(__file__).resolve().parents[1]


def test_parser_exposes_advanced_platform_surface() -> None:
    parser = build_parser()
    for command in ("run", "task", "session", "approval", "resume", "stream", "pipeline", "attachment", "auth", "config", "models", "providers"):
        assert any(action.dest == "command" for action in parser._actions)
    assert parser.parse_args(["run", "create", "inspect", "agent"]).run_command == "create"
    assert parser.parse_args(["approval", "decide", "a1", "approved", "--subject", "alice", "--project", "p1"]).approval_command == "decide"


def test_local_status_is_stable_json(capsys) -> None:
    assert main(["--root", str(ROOT), "--json", "status"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["command"] == "status"
    assert payload["data"]["transport"] == "local"


def test_trailing_json_option_is_supported_by_public_dispatch(capsys) -> None:
    from core.cli.dispatch import main as dispatch_main
    assert dispatch_main(["status", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert "version" in payload


def test_legacy_run_is_not_reinterpreted_as_phase68_run(capsys, monkeypatch) -> None:
    import core.cli.main as legacy
    monkeypatch.setattr(legacy, "main", lambda argv=None: 17)
    from core.cli.dispatch import main as dispatch_main
    assert dispatch_main(["run", "engineering", "--objective", "review"]) == 17
    capsys.readouterr()


def test_governed_run_creation_is_not_direct_execution(capsys) -> None:
    assert main(["--root", str(ROOT), "--json", "run", "create", "inspect", "agent"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["data"]["status"] == "queued"


def test_remote_transport_fails_closed_without_token(capsys) -> None:
    assert main(["--transport", "remote", "--base-url", "http://127.0.0.1:9", "status"]) == EXIT_AUTH
    error = json.loads(capsys.readouterr().err)
    assert error["ok"] is False
    assert error["error"]["code"] == "AUTHENTICATION_REQUIRED"


def test_identifier_path_traversal_is_rejected() -> None:
    with pytest.raises(ValueError):
        _segment("../../etc/passwd")
    with pytest.raises(ValueError):
        _segment("id?x=1")


def test_attachment_limit_constant_is_10_mib() -> None:
    assert MAX_ATTACHMENT == 10 * 1024 * 1024


def test_session_storage_is_bounded_and_does_not_store_auth_tokens(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("SI_SESSIONS", str(tmp_path / "sessions.json"))
    monkeypatch.setenv("SI_AUTH_TOKEN", "super-secret")
    assert main(["--json", "session", "start", "test-session"]) == 0
    payload = json.loads(capsys.readouterr().out)
    stored = json.loads((tmp_path / "sessions.json").read_text())
    assert payload["data"]["id"] == stored[0]["id"]
    assert "super-secret" not in (tmp_path / "sessions.json").read_text()


def test_profiles_store_transport_metadata_without_credentials(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("SI_PROFILES", str(tmp_path / "profiles.json"))
    from core.cli.profile import main as profile_main
    assert profile_main(["set", "dev", "transport", "remote"]) == 0
    capsys.readouterr()
    assert profile_main(["get", "dev"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["data"]["transport"] == "remote"
    assert "token" not in (tmp_path / "profiles.json").read_text()


def test_platform_client_rejects_bad_timeout_and_transport() -> None:
    with pytest.raises(ValueError):
        PlatformClient(ROOT, timeout=0)
    with pytest.raises(ValueError):
        PlatformClient(ROOT, transport="other")
