"""Termux runtime readiness and integration boundary."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from core.environments.models import (
    EnvironmentKind,
    EnvironmentReport,
    EnvironmentStatus,
    RequirementResult,
)
from core.provider_intelligence.omniroute import OmniRouteClient, OmniRouteConfig


@dataclass(frozen=True)
class TermuxConfig:
    """Non-secret policy for a Termux runtime."""

    required_commands: tuple[str, ...] = ("git", "python", "curl", "ssh")
    optional_commands: tuple[str, ...] = ("opencode", "node", "npm")
    require_opencode: bool = True
    require_omniroute: bool = False
    omni_route: OmniRouteConfig | None = None


class TermuxRuntime:
    """Detect and validate a Termux execution environment without mutating it."""

    kind = EnvironmentKind.TERMUX

    def __init__(self, config: TermuxConfig | None = None) -> None:
        self.config = config or TermuxConfig()

    @staticmethod
    def is_termux(environ: Mapping[str, str] | None = None) -> bool:
        env = environ or os.environ
        prefix = env.get("PREFIX", "")
        return bool(env.get("TERMUX_VERSION")) or (
            prefix.endswith("/usr") and "/com.termux/" in prefix
        )

    @staticmethod
    def _python_version() -> str:
        return platform.python_version()

    @staticmethod
    def _command(name: str) -> bool:
        return shutil.which(name) is not None

    def _requirements(self) -> tuple[RequirementResult, ...]:
        results: list[RequirementResult] = []
        for command in self.config.required_commands:
            present = self._command(command)
            results.append(
                RequirementResult(
                    name=f"command:{command}",
                    required=True,
                    present=present,
                    detail="available on PATH" if present else "missing from PATH",
                )
            )
        for command in self.config.optional_commands:
            present = self._command(command)
            required = command == "opencode" and self.config.require_opencode
            results.append(
                RequirementResult(
                    name=f"command:{command}",
                    required=required,
                    present=present,
                    detail="available on PATH" if present else "not installed or not on PATH",
                )
            )
        pkg_present = self._command("pkg")
        results.append(
            RequirementResult(
                name="command:pkg",
                required=True,
                present=pkg_present,
                detail="Termux package manager available" if pkg_present else "pkg not found",
            )
        )
        return tuple(results)

    def doctor(self, environ: Mapping[str, str] | None = None) -> EnvironmentReport:
        """Produce a sanitized readiness report; never writes files or credentials."""
        env = environ or os.environ
        termux = self.is_termux(env)
        requirements = self._requirements() if termux else (
            RequirementResult("environment:termux", True, False, "not running under Termux"),
        )
        open_code_available = self._command("opencode")
        omni_configured = bool(env.get("OMNIROUTE_API_KEY")) or self.config.omni_route is not None
        omni_healthy: bool | None = None
        if self.config.require_omniroute and self.config.omni_route is not None:
            omni_healthy = OmniRouteClient(self.config.omni_route).health().healthy
        elif self.config.require_omniroute:
            omni_healthy = False

        blocking = any(item.blocking for item in requirements)
        if not termux:
            status = EnvironmentStatus.UNSUPPORTED
        elif blocking or (self.config.require_omniroute and omni_healthy is not True):
            status = EnvironmentStatus.DEGRADED
        elif self.config.require_opencode and not open_code_available:
            status = EnvironmentStatus.DEGRADED
        else:
            status = EnvironmentStatus.READY

        return EnvironmentReport(
            kind=self.kind if termux else EnvironmentKind.UNKNOWN,
            status=status,
            architecture=platform.machine(),
            python_version=self._python_version(),
            home=str(Path(env.get("HOME", "")).expanduser()),
            prefix=env.get("PREFIX", ""),
            requirements=requirements,
            open_code_available=open_code_available,
            omni_route_configured=omni_configured,
            omni_route_healthy=omni_healthy,
        )

    def package_commands(self) -> tuple[tuple[str, ...], ...]:
        """Return a conservative, inspectable package plan; does not execute it."""
        return (
            ("pkg", "update"),
            ("pkg", "install", "-y", "git", "python", "curl", "openssh"),
        )

    def validate_workspace(self, workspace: str | Path) -> Path:
        """Validate an existing workspace without creating or deleting anything."""
        path = Path(workspace).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"workspace does not exist: {path}")
        if not path.is_dir():
            raise NotADirectoryError(f"workspace is not a directory: {path}")
        if not os.access(path, os.R_OK):
            raise PermissionError(f"workspace is not readable: {path}")
        return path.resolve()

    @staticmethod
    def python_ok() -> bool:
        return sys.version_info >= (3, 11)


def main(argv: list[str] | None = None) -> int:
    """Run a read-only Termux doctor suitable for direct shell use."""
    parser = argparse.ArgumentParser(description="Check SI-Agents Termux runtime readiness")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of human-readable output")
    args = parser.parse_args(argv)
    report = TermuxRuntime().doctor()
    if args.json:
        print(json.dumps(report.as_dict(), sort_keys=True))
    else:
        print(f"environment: {report.kind.value}")
        print(f"status: {report.status.value}")
        print(f"architecture: {report.architecture}")
        print(f"python: {report.python_version}")
        print(f"opencode: {'available' if report.open_code_available else 'missing'}")
        print(f"omniroute configured: {'yes' if report.omni_route_configured else 'no'}")
        if report.omni_route_healthy is not None:
            print(f"omniroute healthy: {'yes' if report.omni_route_healthy else 'no'}")
        for item in report.requirements:
            state = "ok" if item.present else "missing"
            marker = "required" if item.required else "optional"
            print(f"{state}: {item.name} ({marker})")
    return {
        EnvironmentStatus.READY: 0,
        EnvironmentStatus.DEGRADED: 2,
        EnvironmentStatus.UNSUPPORTED: 3,
    }[report.status]


if __name__ == "__main__":
    raise SystemExit(main())
