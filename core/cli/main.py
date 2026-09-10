"""User-facing SI-Agents command line interface.

The CLI is an explicit setup/control surface. Read-only commands never execute
arbitrary shell commands; mutating setup/update actions require ``--apply``.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from core.cli.config import SIConfig, config_path, load_config, save_config
from core.environments.codespace import CodespaceRuntime
from core.environments.models import EnvironmentReport, EnvironmentStatus
from core.environments.termux import TermuxRuntime
from core.organization.loader import load_catalog
from core.teams.engine import TeamEngine
from core.teams.loader import load_team_catalog

ROOT = Path(__file__).resolve().parents[2]
AGENT_CATALOG = ROOT / "config" / "agent-catalog.json"
TEAM_CATALOG = ROOT / "config" / "team-catalog.json"


def _runtime() -> TermuxRuntime | CodespaceRuntime:
    if TermuxRuntime.is_termux():
        return TermuxRuntime()
    return CodespaceRuntime()


def _report() -> EnvironmentReport:
    return _runtime().doctor()


def _print_report(report: EnvironmentReport) -> None:
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


def cmd_doctor(args: argparse.Namespace) -> int:
    report = _report()
    if args.json:
        print(json.dumps(report.as_dict(), sort_keys=True))
    else:
        _print_report(report)
    return _exit_code(report.status)


def cmd_status(args: argparse.Namespace) -> int:
    config = load_config()
    report = _report()
    print("SI-Agents")
    print("version: 0.1.0")
    print(f"environment: {report.kind.value} ({report.status.value})")
    print(f"workspace: {config.workspace or os.getcwd()}")
    print(f"OpenCode: {config.opencode_url}")
    print(f"OmniRoute: {config.omniroute_url}")
    print(f"OmniRoute model: {config.omniroute_model or 'not selected'}")
    print(f"config: {config_path()}")
    return _exit_code(report.status)


def cmd_agents(args: argparse.Namespace) -> int:
    catalog = load_catalog(AGENT_CATALOG)
    for division in catalog.all_divisions():
        print(f"[{division.id}] {division.name}")
        for agent in catalog.by_division(division.id):
            implementation = "executable" if agent.implementation else "catalog-only"
            print(f"  {agent.id}: {agent.name} ({agent.status.value}, {implementation})")
    return 0


def cmd_teams(args: argparse.Namespace) -> int:
    registry = load_team_catalog(TEAM_CATALOG)
    for team in registry.all():
        print(f"{team.id}: {team.name}")
        print(f"  {team.description}")
        print(f"  tasks: {', '.join(task.id for task in team.tasks)}")
    return 0


def _setup_plan(report: EnvironmentReport) -> list[tuple[str, ...]]:
    runtime = _runtime()
    if isinstance(runtime, TermuxRuntime):
        return list(runtime.package_commands())
    return list(runtime.toolchain_commands())


def _allowlisted_run(command: tuple[str, ...]) -> None:
    allowed = {"pkg", "apt-get", "python", "python3", "pip", "pip3"}
    if not command or Path(command[0]).name not in allowed:
        raise ValueError(f"refusing non-allowlisted setup command: {' '.join(command)}")
    subprocess.run(command, check=True)


def _opencode_config_path() -> Path:
    return Path.home() / ".config" / "opencode" / "opencode.json"


def _configure_opencode(config: SIConfig, *, apply: bool) -> tuple[bool, str]:
    if not config.omniroute_model:
        return False, "an explicit --model is required before configuring an OpenCode OmniRoute provider"
    target = _opencode_config_path()
    if not target.exists():
        payload: dict[str, object] = {"$schema": "https://opencode.ai/config.json"}
    else:
        try:
            payload = json.loads(target.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return False, f"OpenCode config is not plain JSON/contains comments: {target} ({exc})"
        if not isinstance(payload, dict):
            return False, f"OpenCode config must be a JSON object: {target}"

    providers = payload.setdefault("providers", {})
    if not isinstance(providers, dict):
        return False, "OpenCode 'providers' must be an object"
    provider = providers.setdefault("omniroute", {})
    if not isinstance(provider, dict):
        return False, "OpenCode 'providers.omniroute' must be an object"
    provider.update(
        {
            "name": "OmniRoute",
            "package": "@opencode/ai/providers/openai-compatible",
            "settings": {"baseURL": config.omniroute_url.rstrip("/") + "/v1"},
            "models": {
                config.omniroute_model: {
                    "name": config.omniroute_model,
                    "modelID": config.omniroute_model,
                }
            },
        }
    )
    message = f"OpenCode OmniRoute provider {'would be updated' if not apply else 'updated'} at {target}"
    if not apply:
        return True, message
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return True, message


def cmd_setup(args: argparse.Namespace) -> int:
    report = _report()
    config = load_config()
    updated = SIConfig(
        environment=report.kind.value,
        workspace=config.workspace or os.getcwd(),
        opencode_url=args.opencode_url or config.opencode_url,
        omniroute_url=args.omniroute_url or config.omniroute_url,
        omniroute_model=args.model or config.omniroute_model,
    )
    print("setup plan:")
    for command in _setup_plan(report):
        print("  " + " ".join(command))
    print(f"  persist non-secret SI config: {config_path()}")
    if args.configure_opencode:
        print(f"  configure OpenCode provider: {_opencode_config_path()}")

    if not args.apply:
        print("dry-run only; use --apply to perform allowlisted setup and configuration")
        return 0 if report.status is not EnvironmentStatus.UNSUPPORTED else 3

    if report.status is EnvironmentStatus.UNSUPPORTED:
        print("refusing setup in an unsupported environment", file=sys.stderr)
        return 3
    for command in _setup_plan(report):
        _allowlisted_run(command)
    save_config(updated)
    if args.configure_opencode:
        ok, message = _configure_opencode(updated, apply=True)
        print(message)
        if not ok:
            return 2
    print(f"configured: {config_path()}")
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    command = (sys.executable, "-m", "pip", "install", "--upgrade", "si-agents")
    print("update plan: " + " ".join(command))
    if not args.apply:
        print("dry-run only; use --apply to update the installed package")
        return 0
    subprocess.run(command, check=True)
    return 0


def _worker_resolver(agent_id: str):
    catalog = load_catalog(AGENT_CATALOG)
    definition = catalog.get(agent_id)
    if not definition.implementation:
        raise ValueError(f"agent {agent_id} is catalog-only and cannot be executed")
    module_name, class_name = definition.implementation.rsplit(".", 1)
    module = __import__(module_name, fromlist=[class_name])
    return getattr(module, class_name)()


def cmd_run(args: argparse.Namespace) -> int:
    registry = load_team_catalog(TEAM_CATALOG)
    registry.get(args.team)
    engine = TeamEngine(registry)
    execution = engine.run(args.team, initial_context={"objective": args.objective}, resolve_worker=_worker_resolver)
    print(f"team: {execution.team_id}")
    print(f"status: {execution.status.value}")
    for task_id, status in execution.task_status.items():
        print(f"  {task_id}: {status.value}")
    if execution.errors:
        for error in execution.errors:
            print(f"error: {error}", file=sys.stderr)
    return 0 if execution.status.value == "succeeded" else 2


def _exit_code(status: EnvironmentStatus) -> int:
    return {EnvironmentStatus.READY: 0, EnvironmentStatus.DEGRADED: 2, EnvironmentStatus.UNSUPPORTED: 3}[status]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="si", description="SI-Agents control and setup CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    doctor = sub.add_parser("doctor", help="check environment readiness")
    doctor.add_argument("--json", action="store_true")
    doctor.set_defaults(handler=cmd_doctor)

    status = sub.add_parser("status", help="show runtime and configuration status")
    status.set_defaults(handler=cmd_status)

    agents = sub.add_parser("agents", help="list the canonical agent catalog")
    agents.set_defaults(handler=cmd_agents)

    teams = sub.add_parser("teams", help="list canonical teams and workflows")
    teams.set_defaults(handler=cmd_teams)

    setup = sub.add_parser("setup", help="plan or apply safe local setup")
    setup.add_argument("--apply", action="store_true", help="perform allowlisted local setup")
    setup.add_argument("--configure-opencode", action="store_true", help="add/update an OmniRoute provider in OpenCode JSON config")
    setup.add_argument("--opencode-url")
    setup.add_argument("--omniroute-url")
    setup.add_argument("--model", help="explicit OmniRoute model ID for OpenCode configuration")
    setup.set_defaults(handler=cmd_setup)

    update = sub.add_parser("update", help="plan or apply package update")
    update.add_argument("--apply", action="store_true", help="upgrade the installed si-agents package")
    update.set_defaults(handler=cmd_update)

    run = sub.add_parser("run", help="execute a canonical governed team")
    run.add_argument("team", help="team/workflow identifier")
    run.add_argument("--objective", required=True, help="objective passed as initial workflow context")
    run.set_defaults(handler=cmd_run)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"si: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
