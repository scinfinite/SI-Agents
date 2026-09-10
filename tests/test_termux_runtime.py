"""Tests for Termux environment readiness."""

from __future__ import annotations

from pathlib import Path

from core.environments import EnvironmentKind, EnvironmentStatus, TermuxRuntime
from core.environments.termux import TermuxConfig


def test_termux_detection_uses_environment_markers():
    assert TermuxRuntime.is_termux(
        {"TERMUX_VERSION": "0.118.3", "PREFIX": "/data/data/com.termux/files/usr"}
    )
    assert not TermuxRuntime.is_termux({"PREFIX": "/usr"})


def test_doctor_fails_closed_outside_termux(monkeypatch):
    runtime = TermuxRuntime()
    monkeypatch.setattr("core.environments.termux.shutil.which", lambda _: "/bin/tool")
    report = runtime.doctor({"HOME": "/tmp", "PREFIX": "/usr"})
    assert report.kind is EnvironmentKind.UNKNOWN
    assert report.status is EnvironmentStatus.UNSUPPORTED
    assert not report.ready


def test_doctor_can_be_ready_with_required_commands(monkeypatch):
    runtime = TermuxRuntime()
    commands = {"git", "python", "curl", "ssh", "opencode", "pkg"}
    monkeypatch.setattr(
        "core.environments.termux.shutil.which",
        lambda name: f"/mock/{name}" if name in commands else None,
    )
    report = runtime.doctor(
        {
            "TERMUX_VERSION": "0.118.3",
            "PREFIX": "/data/data/com.termux/files/usr",
            "HOME": "/data/data/com.termux/files/home",
        }
    )
    assert report.kind is EnvironmentKind.TERMUX
    assert report.status is EnvironmentStatus.READY
    assert report.open_code_available is True


def test_doctor_requires_opencode_when_configured(monkeypatch):
    runtime = TermuxRuntime(TermuxConfig(require_opencode=True))
    commands = {"git", "python", "curl", "ssh", "pkg"}
    monkeypatch.setattr(
        "core.environments.termux.shutil.which",
        lambda name: f"/mock/{name}" if name in commands else None,
    )
    report = runtime.doctor(
        {"TERMUX_VERSION": "0.118.3", "PREFIX": "/data/data/com.termux/files/usr"}
    )
    assert report.status is EnvironmentStatus.DEGRADED
    assert any(item.name == "command:opencode" for item in report.blocking_requirements)


def test_doctor_can_require_healthy_omniroute(monkeypatch):
    runtime = TermuxRuntime(
        TermuxConfig(
            require_omniroute=True,
            omni_route=__import__(
                "core.provider_intelligence.omniroute", fromlist=["OmniRouteConfig"]
            ).OmniRouteConfig("http://127.0.0.1:20128"),
        )
    )
    commands = {"git", "python", "curl", "ssh", "opencode", "pkg"}
    monkeypatch.setattr(
        "core.environments.termux.shutil.which",
        lambda name: f"/mock/{name}" if name in commands else None,
    )
    monkeypatch.setattr(
        "core.environments.termux.OmniRouteClient.health",
        lambda self: type("Health", (), {"healthy": True})(),
    )
    report = runtime.doctor({"TERMUX_VERSION": "0.118.3", "PREFIX": "/data/data/com.termux/files/usr"})
    assert report.omni_route_healthy is True
    assert report.status is EnvironmentStatus.READY


def test_package_plan_is_non_executing():
    plan = TermuxRuntime().package_commands()
    assert plan[0] == ("pkg", "update")
    assert plan[1][:3] == ("pkg", "install", "-y")


def test_workspace_validation_is_read_only(tmp_path):
    runtime = TermuxRuntime()
    workspace = tmp_path / "project"
    workspace.mkdir()
    assert runtime.validate_workspace(workspace) == Path(workspace).resolve()
