"""Dispatch the stable ``si`` command to legacy commands and operator surfaces."""

from __future__ import annotations

import sys

from core.deployment_center.cli import main as deployment_main
from core.hardening.cli import main as verify_main
from core.tui.cli import main as tui_main
from core.web.cli import main as web_main

ADVANCED_COMMANDS = {
    "workflows", "organization", "memory", "governance", "evidence", "environments",
    "harnesses", "settings", "visualization", "events", "logs", "task", "execution",
    "approval", "attachment", "auth", "config", "profile", "models", "providers",
    "stream", "resume", "pipeline", "agent", "team", "workflow",
}
GLOBAL_VALUE_OPTIONS = {"--root", "--transport", "--base-url", "--token-env", "--timeout"}
GLOBAL_FLAGS = {"--json", "--pretty"}


def _normalize_global_options(arguments: list[str]) -> list[str]:
    """Allow global options before or after a command without ambiguity."""
    prefix: list[str] = []
    body: list[str] = []
    index = 0
    while index < len(arguments):
        token = arguments[index]
        if token in GLOBAL_FLAGS:
            prefix.append(token)
            index += 1
            continue
        if token in GLOBAL_VALUE_OPTIONS:
            if index + 1 >= len(arguments):
                body.extend(arguments[index:])
                break
            prefix.extend((token, arguments[index + 1]))
            index += 2
            continue
        body.append(token)
        index += 1
    return prefix + body


def _first_command(arguments: list[str]) -> str | None:
    index = 0
    while index < len(arguments):
        token = arguments[index]
        if token in GLOBAL_FLAGS:
            index += 1
            continue
        if token in GLOBAL_VALUE_OPTIONS:
            index += 2
            continue
        return token
    return None


def _task_alias(arguments: list[str]) -> list[str]:
    if len(arguments) >= 2 and arguments[0] == "task" and arguments[1] == "create":
        return ["run", "create", *arguments[2:]]
    return arguments


def main(argv: list[str] | None = None) -> int:
    original = list(sys.argv[1:] if argv is None else argv)
    command = _first_command(original)
    arguments = _normalize_global_options(original) if command in ADVANCED_COMMANDS or command in {"session", "agent", "team", "workflow"} else original
    if command == "web":
        return web_main(arguments[arguments.index("web") + 1:] if "web" in arguments else [])
    if command == "tui":
        return tui_main(arguments[arguments.index("tui") + 1:] if "tui" in arguments else [])
    if command in {"deploy", "deployment"}:
        return deployment_main(arguments[arguments.index(command) + 1:])
    if command in {"verify", "validate-release"}:
        return verify_main(arguments[arguments.index(command) + 1:])
    if command in {"agent", "team", "workflow"}:
        from core.cli.aliases import main as alias_main
        return alias_main(command, [token for token in arguments if token != command])
    arguments = _task_alias(arguments)
    if arguments and arguments[0] == "logs":
        arguments = ["events", *arguments[1:]]
    if arguments and arguments[0] == "profile":
        from core.cli.profile import main as profile_main
        return profile_main(arguments[1:])
    if arguments and arguments[0] == "session":
        from core.cli.session import main as session_main
        return session_main(arguments[1:])
    if arguments and arguments[0] in ADVANCED_COMMANDS:
        from core.cli.platform import main as platform_main
        return platform_main(arguments)
    if arguments and arguments[0] == "run" and len(arguments) > 1 and arguments[1] in {"create", "list", "get"}:
        from core.cli.platform import main as platform_main
        return platform_main(arguments)
    from core.cli.main import main as legacy_main
    return legacy_main(arguments)


if __name__ == "__main__":
    raise SystemExit(main())