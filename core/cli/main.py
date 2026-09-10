"""User-facing SI-Agents command line interface.

The CLI is an explicit setup/control surface. Read-only commands never execute
arbitrary shell commands; mutating setup/update actions require ``--apply``.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from core.cli.audit import audit_summary
from core.cli.config import SIConfig, config_path, load_config, save_config
from core.environments.codespace import CodespaceRuntime
from core.environments.models import EnvironmentReport, EnvironmentStatus
from core.environments.termux import TermuxRuntime
from core.handoff.service import create_handoff, resume_context
from core.handoff.store import HandoffStore
from core.organization.loader import load_catalog
from core.personas.registry import PersonaRegistry
from core.teams.engine import TeamEngine
from core.teams.loader import load_team_catalog

ROOT = Path(__file__).resolve().parents[2]


def _package_version() -> str:
    try:
        return version("si-agents")
    except PackageNotFoundError:
        return "0.1.0"


def _catalog_path(filename: str) -> Path:
    source_path = ROOT / "config" / filename
    if source_path.exists():
        return source_path
    installed_path = Path(sys.prefix) / "share" / "si-agents" / "config" / filename
    if installed_path.exists():
        return installed_path
    raise FileNotFoundError(f"canonical catalog not found: {filename}")


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
    payload = {
        "version": _package_version(),
        "environment": report.kind.value,
        "environment_status": report.status.value,
        "workspace": config.workspace or os.getcwd(),
        "opencode_url": config.opencode_url,
        "omniroute_url": config.omniroute_url,
        "omniroute_model": config.omniroute_model,
        "config": str(config_path()),
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("SI-Agents")
        print(f"version: {payload['version']}")
        print(f"environment: {payload['environment']} ({payload['environment_status']})")
        print(f"workspace: {payload['workspace']}")
        print(f"OpenCode: {payload['opencode_url']}")
        print(f"OmniRoute: {payload['omniroute_url']}")
        print(f"OmniRoute model: {payload['omniroute_model'] or 'not selected'}")
        print(f"config: {payload['config']}")
    return _exit_code(report.status)


def _agent_payload(agent) -> dict[str, object]:
    return {
        "id": agent.id,
        "name": agent.name,
        "division": agent.division,
        "description": agent.description,
        "status": agent.status.value,
        "implementation": agent.implementation,
        "skills": list(agent.skills),
        "capabilities": list(agent.capabilities),
        "permissions": list(agent.permissions),
        "harnesses": list(agent.harnesses),
        "environments": list(agent.environments),
    }


def cmd_agents(args: argparse.Namespace) -> int:
    catalog = load_catalog(_catalog_path("agent-catalog.json"))
    agents = list(catalog.all())
    if args.division:
        agents = list(catalog.by_division(args.division))
    if args.status:
        agents = [agent for agent in agents if agent.status.value == args.status]
    if args.search:
        needle = args.search.casefold()
        agents = [
            agent for agent in agents
            if needle in agent.id.casefold()
            or needle in agent.name.casefold()
            or needle in agent.description.casefold()
        ]
    agents.sort(key=lambda agent: (agent.division, agent.name, agent.id))
    if args.json:
        print(json.dumps([_agent_payload(agent) for agent in agents], indent=2, sort_keys=True))
        return 0
    for division in catalog.all_divisions():
        division_agents = [agent for agent in agents if agent.division == division.id]
        if not division_agents:
            continue
        print(f"[{division.id}] {division.name} ({len(division_agents)})")
        for agent in division_agents:
            implementation = "executable" if agent.implementation else "catalog-only"
            print(f"  {agent.id}: {agent.name} ({agent.status.value}, {implementation})")
    return 0


def cmd_teams(args: argparse.Namespace) -> int:
    registry = load_team_catalog(_catalog_path("team-catalog.json"))
    teams = list(registry.all())
    if args.search:
        needle = args.search.casefold()
        teams = [
            team for team in teams
            if needle in team.id.casefold()
            or needle in team.name.casefold()
            or needle in team.description.casefold()
        ]
    teams.sort(key=lambda team: team.id)
    if args.json:
        payload = [
            {
                "id": team.id,
                "name": team.name,
                "description": team.description,
                "tasks": [task.id for task in team.tasks],
            }
            for team in teams
        ]
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    for team in teams:
        print(f"{team.id}: {team.name}")
        print(f"  {team.description}")
        print(f"  tasks: {', '.join(task.id for task in team.tasks)}")
    return 0


def cmd_personas(args: argparse.Namespace) -> int:
    registry = PersonaRegistry()
    personas = registry.load_directory(ROOT / "agents")
    if args.division:
        personas = tuple(persona for persona in personas if persona.division == args.division)
    if args.search:
        needle = args.search.casefold()
        personas = tuple(
            persona for persona in personas
            if needle in persona.id.casefold() or needle in persona.name.casefold()
        )
    personas = tuple(sorted(personas, key=lambda persona: (persona.division, persona.name, persona.id)))
    if args.json:
        print(json.dumps([persona.as_dict() for persona in personas], indent=2, sort_keys=True))
    else:
        for persona in personas:
            print(f"{persona.id}: {persona.name} [{persona.division}]")
    return 0


def cmd_audit(args: argparse.Namespace) -> int:
    payload = audit_summary(ROOT)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"repository audit: {'PASS' if payload['ok'] else 'FAIL'}")
        for check in payload["checks"]:
            state = "ok" if check["ok"] else "FAIL"
            print(f"{state}: {check['name']} — {check['detail']}")
    return 0 if payload["ok"] else 2


def _setup_plan(report: EnvironmentReport) -> list[tuple[str, ...]]:
    runtime = _runtime()
    if isinstance(runtime, TermuxRuntime):
        return list(runtime.package_commands())
    return list(runtime.toolchain_commands())


def _allowlisted_run(command: tuple[str, ...]) -> None:
    allowed = {"pkg", "apt-get", "python", "python3", "pip", "pip3", "npm"}
    if not command or Path(command[0]).name not in allowed:
        raise ValueError(f"refusing non-allowlisted setup command: {' '.join(command)}")
    subprocess.run(command, check=True)


def _opencode_install_plan() -> tuple[str, ...] | None:
    if shutil.which("opencode"):
        return None
    if shutil.which("npm"):
        return ("npm", "install", "-g", "opencode-ai")
    return None


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
    install_plan = _opencode_install_plan() if args.install_opencode else None
    print("setup plan:")
    for command in _setup_plan(report):
        print("  " + " ".join(command))
    if args.install_opencode:
        if install_plan:
            print("  " + " ".join(install_plan))
        elif shutil.which("opencode"):
            print("  OpenCode already installed")
        else:
            print("  OpenCode install unavailable: install Node.js/npm first", file=sys.stderr)
    print(f"  persist non-secret SI config: {config_path()}")
    if args.configure_opencode:
        print(f"  configure OpenCode provider: {_opencode_config_path()}")
    if not args.apply:
        print("dry-run only; use --apply to perform allowlisted setup and configuration")
        return 0 if report.status is not EnvironmentStatus.UNSUPPORTED else 3
    if report.status is EnvironmentStatus.UNSUPPORTED:
        print("refusing setup in an unsupported environment", file=sys.stderr)
        return 3
    if args.install_opencode and not shutil.which("opencode") and install_plan is None:
        return 2
    for command in _setup_plan(report):
        _allowlisted_run(command)
    if install_plan:
        _allowlisted_run(install_plan)
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
    catalog = load_catalog(_catalog_path("agent-catalog.json"))
    definition = catalog.get(agent_id)
    if not definition.implementation:
        raise ValueError(f"agent {agent_id} is catalog-only and cannot be executed")
    module_name, class_name = definition.implementation.rsplit(".", 1)
    module = __import__(module_name, fromlist=[class_name])
    return getattr(module, class_name)()


def _environment_name() -> str:
    return _report().kind.value


def cmd_run(args: argparse.Namespace) -> int:
    registry = load_team_catalog(_catalog_path("team-catalog.json"))
    registry.get(args.team)
    initial = {"objective": args.objective}
    if args.handoff:
        envelope = HandoffStore().load(Path(args.handoff))
        initial.update(resume_context(envelope, Path.cwd()))
    engine = TeamEngine(registry)
    execution = engine.run(args.team, initial_context=initial, resolve_worker=_worker_resolver)
    print(f"team: {execution.team_id}")
    print(f"status: {execution.status.value}")
    for task_id, status in execution.task_status.items():
        print(f"  {task_id}: {status.value}")
    if execution.errors:
        for error in execution.errors:
            print(f"error: {error}", file=sys.stderr)
    return 0 if execution.status.value == "succeeded" else 2


def cmd_handoff_create(args: argparse.Namespace) -> int:
    if args.source == args.target:
        print("source and target environments must differ", file=sys.stderr)
        return 2
    registry = load_team_catalog(_catalog_path("team-catalog.json"))
    registry.get(args.team)
    engine = TeamEngine(registry)
    execution = engine.run(args.team, initial_context={"objective": args.objective}, resolve_worker=_worker_resolver)
    envelope = create_handoff(
        execution,
        source_environment=args.source,
        target_environment=args.target,
        workspace=Path.cwd(),
    )
    output = HandoffStore.safe_export_path(Path(args.output))
    output.parent.mkdir(parents=True, exist_ok=True)
    HandoffStore(output.parent).save(envelope)
    stored = output.parent / f"{envelope.handoff_id}.json"
    if stored != output:
        stored.replace(output)
    print(f"handoff: {output}")
    print(f"id: {envelope.handoff_id}")
    print(f"integrity: {envelope.digest()}")
    print(f"status: {execution.status.value}")
    return 0 if execution.status.value == "succeeded" else 2


def cmd_handoff_inspect(args: argparse.Namespace) -> int:
    envelope = HandoffStore().load(Path(args.path))
    if args.json:
        print(json.dumps(envelope.as_dict(), indent=2, sort_keys=True))
    else:
        print(f"handoff: {envelope.handoff_id}")
        print(f"status: {envelope.status.value}")
        print(f"source: {envelope.source_environment}")
        print(f"target: {envelope.target_environment or 'unspecified'}")
        print(f"team: {envelope.team_id or 'not specified'}")
        print(f"execution: {envelope.execution_id or 'not specified'}")
        print(f"integrity: {envelope.digest()}")
        print(f"evidence: {len(envelope.evidence_ids)}")
    return 0


def cmd_handoff_import(args: argparse.Namespace) -> int:
    envelope = HandoffStore().import_file(Path(args.path), target_environment=_environment_name())
    resume_context(envelope, Path.cwd())
    print(f"valid handoff: {envelope.handoff_id}")
    print(f"source: {envelope.source_environment}")
    print(f"target: {envelope.target_environment}")
    print(f"team: {envelope.team_id or 'not specified'}")
    print(f"execution: {envelope.execution_id or 'not specified'}")
    print(f"evidence: {len(envelope.evidence_ids)}")
    return 0


def _exit_code(status: EnvironmentStatus) -> int:
    return {EnvironmentStatus.READY: 0, EnvironmentStatus.DEGRADED: 2, EnvironmentStatus.UNSUPPORTED: 3}[status]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="si", description="SI-Agents control, audit, and setup CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    doctor = sub.add_parser("doctor", help="check environment readiness")
    doctor.add_argument("--json", action="store_true")
    doctor.set_defaults(handler=cmd_doctor)

    status = sub.add_parser("status", help="show runtime and configuration status")
    status.add_argument("--json", action="store_true")
    status.set_defaults(handler=cmd_status)

    audit = sub.add_parser("audit", help="run read-only repository integrity checks")
    audit.add_argument("--json", action="store_true")
    audit.set_defaults(handler=cmd_audit)

    agents = sub.add_parser("agents", help="list and filter the canonical agent catalog")
    agents.add_argument("--division")
    agents.add_argument("--status", choices=("active", "cataloged", "deprecated"))
    agents.add_argument("--search")
    agents.add_argument("--json", action="store_true")
    agents.set_defaults(handler=cmd_agents)

    personas = sub.add_parser("personas", help="list discovered Markdown personas")
    personas.add_argument("--division")
    personas.add_argument("--search")
    personas.add_argument("--json", action="store_true")
    personas.set_defaults(handler=cmd_personas)

    teams = sub.add_parser("teams", help="list and filter canonical teams and workflows")
    teams.add_argument("--search")
    teams.add_argument("--json", action="store_true")
    teams.set_defaults(handler=cmd_teams)

    setup = sub.add_parser("setup", help="plan or apply safe local setup")
    setup.add_argument("--apply", action="store_true", help="perform allowlisted local setup")
    setup.add_argument("--install-opencode", action="store_true", help="install OpenCode using npm when available")
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
    run.add_argument("--handoff", help="validated handoff JSON to resume context from")
    run.set_defaults(handler=cmd_run)

    handoff = sub.add_parser("handoff", help="transfer verified workflow state between environments")
    handoff_sub = handoff.add_subparsers(dest="handoff_command", required=True)
    create = handoff_sub.add_parser("create", help="execute a team and export a portable handoff")
    create.add_argument("team")
    create.add_argument("--objective", required=True)
    create.add_argument("--source", required=True, choices=("termux", "codespace"))
    create.add_argument("--target", required=True, choices=("termux", "codespace"))
    create.add_argument("--output", required=True)
    create.set_defaults(handler=cmd_handoff_create)
    inspect = handoff_sub.add_parser("inspect", help="verify and inspect a handoff")
    inspect.add_argument("path")
    inspect.add_argument("--json", action="store_true")
    inspect.set_defaults(handler=cmd_handoff_inspect)
    import_cmd = handoff_sub.add_parser("import", help="validate a handoff for this environment")
    import_cmd.add_argument("path")
    import_cmd.set_defaults(handler=cmd_handoff_import)
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
