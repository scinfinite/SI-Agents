"""Singular resource aliases for the Phase 68 CLI platform."""
from __future__ import annotations

from core.cli.platform import main as platform_main


def main(resource: str, argv: list[str] | None = None) -> int:
    args = list(argv or [])
    if not args:
        args = ["list"]
    command = args.pop(0)
    if command not in {"list", "get"}:
        args.insert(0, command)
        command = "list"
    if command == "get":
        if not args:
            raise ValueError(f"{resource} get requires an id")
        identifier = args.pop(0)
        args.extend(["--search", identifier])
    plural = {"agent": "agents", "team": "teams", "workflow": "workflows"}[resource]
    return platform_main([plural, *args])
