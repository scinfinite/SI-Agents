"""Command-line deployment planning surface; no apply operation is exposed."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .api import create, snapshot
from .service import DeploymentCenter


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="si-deploy")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("targets")
    sub.add_parser("plans")
    plan = sub.add_parser("plan")
    plan.add_argument("id")
    plan.add_argument("harness_id")
    args = parser.parse_args(argv)
    data = snapshot(DeploymentCenter(Path(args.root).resolve()))
    if args.command == "targets":
        data = {"targets": data["targets"]}
    elif args.command == "plans":
        data = {"plans": data["plans"]}
    else:
        data = create(DeploymentCenter(Path(args.root).resolve()), {"id": args.id, "harness_id": args.harness_id})
    print(json.dumps(data, indent=2, sort_keys=True) if args.json else json.dumps(data, sort_keys=True))
    return 0
