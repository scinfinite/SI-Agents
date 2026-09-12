"""Bounded, non-secret CLI transport profiles."""
from __future__ import annotations

import json
import os
from pathlib import Path

MAX_PROFILES = 32
ALLOWED_KEYS = {"base_url", "transport", "token_env", "root"}


def _path() -> Path:
    return Path(os.environ.get("SI_PROFILES", "~/.config/si-agents/profiles.json")).expanduser()


def _load() -> dict[str, dict[str, str]]:
    path = _path()
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("profile store must be a JSON object")
    return {
        str(name): {str(k): str(v) for k, v in value.items() if k in ALLOWED_KEYS}
        for name, value in list(data.items())[:MAX_PROFILES]
        if isinstance(name, str) and isinstance(value, dict)
    }


def _save(data: dict[str, dict[str, str]]) -> None:
    if len(data) > MAX_PROFILES:
        raise ValueError(f"at most {MAX_PROFILES} profiles are supported")
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.parent.chmod(0o700)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    path.chmod(0o600)


def main(argv: list[str] | None = None) -> int:
    args = list(argv or [])
    command = args.pop(0) if args else "list"
    profiles = _load()
    if command == "list":
        print(json.dumps({"ok": True, "command": "profile.list", "data": sorted(profiles)}, sort_keys=True))
        return 0
    if command == "get":
        if not args or args[0] not in profiles:
            raise ValueError("profile not found")
        print(json.dumps({"ok": True, "command": "profile.get", "data": profiles[args[0]]}, sort_keys=True))
        return 0
    if command == "set":
        if len(args) != 3 or args[1] not in ALLOWED_KEYS:
            raise ValueError("usage: profile set <name> <key> <value>")
        name, key, value = args
        if not value or len(name) > 64 or any(ch in name for ch in "/\\\n\r"):
            raise ValueError("invalid profile name/value")
        if key == "transport" and value not in {"local", "remote"}:
            raise ValueError("transport must be local or remote")
        profiles.setdefault(name, {})[key] = value
        _save(profiles)
        print(json.dumps({"ok": True, "command": "profile.set", "data": {"name": name, "key": key, "value": value}}, sort_keys=True))
        return 0
    raise ValueError("unknown profile command")
