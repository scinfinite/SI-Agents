"""Launcher for the local Web Control Center."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from core.control_api.service import ControlApiService

from .models import WebConfig
from .server import serve


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="si-web", description="Run the SI-Agents local Web surface")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8788)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--allow-remote", action="store_true")
    parser.add_argument("--auth-token-env", default="SI_WEB_AUTH_TOKEN")
    parser.add_argument("--cors-origin", action="append", default=[])
    parser.add_argument("--audit-log", type=Path)
    args = parser.parse_args(argv)
    token = os.environ.get(args.auth_token_env)
    config = WebConfig(host=args.host, port=args.port, allow_remote=args.allow_remote, auth_token=token, audit_log=args.audit_log, cors_origins=tuple(args.cors_origin))
    config.validate()
    serve(config, ControlApiService(args.root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
