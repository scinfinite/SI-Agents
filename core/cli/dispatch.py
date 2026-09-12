"""Dispatch the stable ``si`` command to legacy commands and operator surfaces."""

from __future__ import annotations

import sys

from core.deployment_center.cli import main as deployment_main
from core.hardening.cli import main as verify_main
from core.tui.cli import main as tui_main
from core.web.cli import main as web_main

ADVANCED_COMMANDS = {
    "status", "agents", "teams", "workflows", "organization", "skills", "memory",
    "governance", "evidence", "environments", "harnesses", "settings", "visualization",
    "events", "run", "task", "execution", "approval", "session", "attachment", "auth",
    "config", "models", "providers", "stream", "resume", "pipeline",
}


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments and arguments[0] == "web":
        return web_main(arguments[1:])
    if arguments and arguments[0] == "tui":
        return tui_main(arguments[1:])
    if arguments and arguments[0] in {"deploy", "deployment"}:
        return deployment_main(arguments[1:])
    if arguments and arguments[0] in {"verify", "validate-release"}:
        return verify_main(arguments[1:])
    if arguments and arguments[0] in ADVANCED_COMMANDS:
        from core.cli.platform import main as platform_main

        return platform_main(arguments)
    from core.cli.main import main as legacy_main

    return legacy_main(arguments)


if __name__ == "__main__":
    raise SystemExit(main())
