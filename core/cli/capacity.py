"""Operator-facing capacity profile helper."""

from __future__ import annotations

import argparse
import json
import os

from core.capacity import CapacityLevel, CapacityPolicy, detect_environment


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="si-capacity", description="Select bounded SI-Agents execution capacity")
    parser.add_argument("level", choices=[level.value for level in CapacityLevel], nargs="?", default=os.environ.get("SI_CAPACITY", "low" if detect_environment() == "termux" else "medium"))
    parser.add_argument("--workers", type=int)
    parser.add_argument("--workload", default="general")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    decision = CapacityPolicy().decide(args.level, workers=args.workers, workload=args.workload)
    if args.json:
        print(json.dumps(decision.as_dict(), indent=2, sort_keys=True))
    else:
        print(f"environment: {detect_environment()}")
        print(f"capacity: {decision.level.value}")
        print(f"workers: {decision.workers}")
        print(f"allowed: {'yes' if decision.allowed else 'no'}")
        if decision.warning:
            print(f"warning: {decision.warning}")
        if decision.reason:
            print(f"reason: {decision.reason}")
    return 0 if decision.allowed else 3


if __name__ == "__main__":
    raise SystemExit(main())
