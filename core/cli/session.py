"""Client-owned session metadata command surface."""
from __future__ import annotations

import argparse
import hashlib
import time
from pathlib import Path

from core.cli.platform import _finish, _load_sessions, _save_sessions


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="si session")
    parser.add_argument("--root", default=".")
    parser.add_argument("--transport", choices=("local", "remote"), default="local")
    parser.add_argument("--base-url", default="")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--pretty", action="store_true")
    sub = parser.add_subparsers(dest="session_command", required=True)
    start = sub.add_parser("start")
    start.add_argument("name")
    start.set_defaults(handler="start")
    listed = sub.add_parser("list")
    listed.set_defaults(handler="list")
    got = sub.add_parser("get")
    got.add_argument("session_id")
    got.set_defaults(handler="get")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    sessions = _load_sessions()
    if args.handler == "start":
        item = {
            "id": hashlib.sha256(f"{time.time_ns()}:{args.name}".encode()).hexdigest()[:24],
            "name": args.name,
            "transport": args.transport,
            "base_url": args.base_url or None,
            "workspace": str(Path(args.root).resolve()),
            "created_at": int(time.time()),
        }
        sessions.append(item)
        _save_sessions(sessions)
        return _finish(args, item, "session.start")
    if args.handler == "list":
        return _finish(args, sessions, "session.list")
    for item in sessions:
        if item.get("id") == args.session_id:
            return _finish(args, item, "session.get")
    raise KeyError(args.session_id)
