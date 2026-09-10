"""Persistent, non-secret configuration for the ``si`` CLI."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any


@dataclass(frozen=True)
class SIConfig:
    """User configuration; secrets are intentionally excluded from this model."""

    environment: str | None = None
    workspace: str | None = None
    opencode_url: str = "http://127.0.0.1:4096"
    omniroute_url: str = "http://127.0.0.1:20128"
    omniroute_model: str | None = None


def config_path(environ: dict[str, str] | None = None) -> Path:
    env = environ or os.environ
    explicit = env.get("SI_CONFIG")
    if explicit:
        return Path(explicit).expanduser()
    xdg = env.get("XDG_CONFIG_HOME")
    base = Path(xdg).expanduser() if xdg else Path.home() / ".config"
    return base / "si-agents" / "config.json"


def load_config(path: Path | None = None) -> SIConfig:
    target = path or config_path()
    if not target.exists():
        return SIConfig()
    payload: Any = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"invalid SI configuration: {target}")
    allowed = {"environment", "workspace", "opencode_url", "omniroute_url", "omniroute_model"}
    unknown = set(payload) - allowed
    if unknown:
        raise ValueError(f"unknown SI configuration keys: {', '.join(sorted(unknown))}")
    return SIConfig(**{key: value for key, value in payload.items()})


def save_config(config: SIConfig, path: Path | None = None) -> Path:
    target = path or config_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.parent.chmod(0o700)
    data = json.dumps(asdict(config), indent=2, sort_keys=True) + "\n"
    with NamedTemporaryFile("w", encoding="utf-8", dir=target.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    temporary.chmod(0o600)
    temporary.replace(target)
    return target
