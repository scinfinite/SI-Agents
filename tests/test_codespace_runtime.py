from __future__ import annotations

from pathlib import Path

import pytest

from core.environments import CodespaceConfig, CodespaceRuntime, EnvironmentKind, EnvironmentStatus


def test_codespace_detection() -> None:
    assert CodespaceRuntime.is_codespace({"CODESPACES": "true"})
    assert CodespaceRuntime.is_codespace({"GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN": "example"})
    assert not CodespaceRuntime.is_codespace({"CODESPACES": "false"})


def test_non_codespace_is_unsupported(monkeypatch: pytest.MonkeyPatch) -> None:
    runtime = CodespaceRuntime()
    monkeypatch.setattr(runtime, "_command", staticmethod(lambda _: True))
    report = runtime.doctor({"CODESPACES": "false", "HOME": "/tmp"})
    assert report.kind is EnvironmentKind.UNKNOWN
    assert report.status is EnvironmentStatus.UNSUPPORTED


def test_codespace_missing_opencode_is_degraded(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    runtime = CodespaceRuntime()
    monkeypatch.setattr(runtime, "_command", staticmethod(lambda name: name != "opencode"))
    report = runtime.doctor(
        {
            "CODESPACES": "true",
            "HOME": str(tmp_path),
            "GITHUB_WORKSPACE": str(tmp_path),
        }
    )
    assert report.kind is EnvironmentKind.CODESPACE
    assert report.status is EnvironmentStatus.DEGRADED
    assert not report.open_code_available
    assert any(item.name == "command:opencode" and item.blocking for item in report.requirements)


def test_codespace_ready_when_required_dependencies_exist(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    runtime = CodespaceRuntime()
    monkeypatch.setattr(runtime, "_command", staticmethod(lambda _: True))
    report = runtime.doctor(
        {
            "CODESPACES": "true",
            "HOME": str(tmp_path),
            "GITHUB_WORKSPACE": str(tmp_path),
        }
    )
    assert report.ready
    assert report.kind is EnvironmentKind.CODESPACE


def test_github_cli_can_be_required() -> None:
    runtime = CodespaceRuntime(CodespaceConfig(require_github_cli=True))
    assert runtime.config.require_github_cli


def test_package_or_toolchain_plan_is_non_executing() -> None:
    plan = CodespaceRuntime().toolchain_commands()
    assert plan == (
        ("python", "--version"),
        ("git", "--version"),
        ("curl", "--version"),
        ("ssh", "-V"),
        ("opencode", "--version"),
    )


def test_workspace_validation(tmp_path: Path) -> None:
    runtime = CodespaceRuntime()
    assert runtime.validate_workspace(tmp_path) == tmp_path.resolve()
    with pytest.raises(FileNotFoundError):
        runtime.validate_workspace(tmp_path / "missing")
    file_path = tmp_path / "file"
    file_path.write_text("x", encoding="utf-8")
    with pytest.raises(NotADirectoryError):
        runtime.validate_workspace(file_path)


def test_report_is_secret_free(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    runtime = CodespaceRuntime()
    monkeypatch.setattr(runtime, "_command", staticmethod(lambda _: True))
    secret = "super-secret-api-key"
    report = runtime.doctor(
        {
            "CODESPACES": "true",
            "HOME": str(tmp_path),
            "GITHUB_WORKSPACE": str(tmp_path),
            "OMNIROUTE_API_KEY": secret,
        }
    )
    assert secret not in str(report.as_dict())
    assert report.omni_route_configured
