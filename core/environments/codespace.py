"""GitHub Codespaces runtime readiness and integration boundary."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
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
class CodespaceConfig:
    """Non-secret policy for a GitHub Codespaces runtime."""

    required_commands: tuple[str, ...] = ("git", "python", "curl", "ssh")
    optional_commands: tuple[str, ...] = ("opencode", "gh", "node", "npm")
    require_opencode: bool = True
    require_github_cli: bool = False
    require_omniroute: bool = False
    omni_route: OmniRouteConfig | None = None


class CodespaceRuntime:
    """Detect and validate a Codespaces environment without mutating it."""

    kind = EnvironmentKind.CODESPACE

    def __init__(self, config: CodespaceConfig | None = None) -> None:
        self.config = config or CodespaceConfig()

    @staticmethod
    def is_codespace(environ: Mapping[str, str] | None = None) -> bool:
        env = environ or os.environ
        return env.get("CODESPACES", "").lower() == "true" or bool(
            env.get("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN")
        )

    @staticmethod
    def _command(name: str) -> bool:
        return shutil.which(name) is not None

    def _requirements(self, env: Mapping[str, str]) -> tuple[RequirementResult, ...]:
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
            required = (command == "opencode" and self.config.require_opencode) or (
                command == "gh" and self.config.require_github_cli
            )
            results.append(
                RequirementResult(
                    name=f"command:{command}",
                    required=required,
                    present=present,
                    detail="available on PATH" if present else "not installed or not on PATH",
                )
            )
        workspace = env.get("GITHUB_WORKSPACE") or env.get("WORKSPACE_FOLDER") or "/workspaces"
        workspace_path = Path(workspace).expanduser()
        results.append(
            RequirementResult(
                name="workspace:codespace",
                required=True,
                present=workspace_path.is_dir() and os.access(workspace_path, os.R_OK),
                detail=(
                    "workspace exists and is readable"
                    if workspace_path.is_dir() and os.access(workspace_path, os.R_OK)
                    else "Codespace workspace is missing or unreadable"
                ),
            )
        )
        return tuple(results)

    def doctor(self, environ: Mapping[str, str] | None = None) -> EnvironmentReport:
        """Produce a sanitized readiness report; never writes files or credentials."""
        env = environ or os.environ
        codespace = self.is_codespace(env)
        requirements = self._requirements(env) if codespace else (
            RequirementResult("environment:codespace", True, False, "not running in GitHub Codespaces"),
        )
        open_code_available = self._command("opencode")
        omni_configured = bool(env.get("OMNIROUTE_API_KEY")) or self.config.omni_route is not None
        omni_healthy: bool | None = None
        if self.config.require_omniroute and self.config.omni_route is not None:
            omni_healthy = OmniRouteClient(self.config.omni_route).health().healthy
        elif self.config.require_omniroute:
            omni_healthy = False

        blocking = any(item.blocking for item in requirements)
        degraded = (
            blocking
            or (self.config.require_omniroute and omni_healthy is not True)
            or (self.config.require_opencode and not open_code_available)
        )
        if not codespace:
            status = EnvironmentStatus.UNSUPPORTED
        elif degraded:
            status = EnvironmentStatus.DEGRADED
        else:
            status = EnvironmentStatus.READY

        return EnvironmentReport(
            kind=self.kind if codespace else EnvironmentKind.UNKNOWN,
            status=status,
            architecture=platform.machine(),
            python_version=platform.python_version(),
            home=str(Path(env.get("HOME", "")).expanduser()),
            prefix=env.get("PATH", "").split(os.pathsep)[0] if env.get("PATH") else "",
            requirements=requirements,
            open_code_available=open_code_available,
            omni_route_configured=omni_configured,
            omni_route_healthy=omni_healthy,
        )

    def toolchain_commands(self) -> tuple[tuple[str, ...], ...]:
        """Return an inspectable, non-executing Codespaces toolchain plan."""
        return (
            ("python", "--version"),
            ("git", "--version"),
            ("curl", "--version"),
            ("ssh", "-V"),
            ("opencode", "--version"),
        )

    def validate_workspace(self, workspace: str | Path) -> Path:
        """Validate an existing Codespace workspace without mutation."""
        path = Path(workspace).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"workspace does not exist: {path}")
        if not path.is_dir():
            raise NotADirectoryError(f"workspace is not a directory: {path}")
        if not os.access(path, os.R_OK):
            raise PermissionError(f"workspace is not readable: {path}")
        return path.resolve()


def main(argv: list[str] | None = None) -> int:
    """Run a read-only Codespaces doctor suitable for direct shell use."""
    parser = argparse.ArgumentParser(description="Check SI-Agents Codespaces runtime readiness")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of human-readable output")
    args = parser.parse_args(argv)
    report = CodespaceRuntime().doctor()
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
    return {EnvironmentStatus.READY: 0, EnvironmentStatus.DEGRADED: 2, EnvironmentStatus.UNSUPPORTED: 3}[report.status]


if __name__ == "__main__":
    raise SystemExit(main())
