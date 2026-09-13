"""CLI surface for SI-Agents workload-capacity policy."""
from __future__ import annotations

import argparse
import json

from core.capacity import CapacityPolicy, CapacityTarget


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="si capacity", description="Inspect Low/Medium/High workload limits")
    parser.add_argument("--level", choices=("low", "medium", "high"))
    parser.add_argument("--target", choices=("local", "termux", "desktop", "codespace", "remote"))
    parser.add_argument("--action", default="status")
    parser.add_argument("--compile", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    policy = CapacityPolicy()
    payload = {"action": args.action, "compile": args.compile}
    if args.level:
        payload["capacity"] = args.level
    target = CapacityTarget(args.target) if args.target else None
    decision = policy.evaluate(payload, target=target)
    result = {"policy": policy.describe(), "decision": decision.as_dict()}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"capacity: {decision.level.value}")
        print(f"target: {decision.target.value}")
        print(f"allowed: {'yes' if decision.allowed else 'no'}")
        print(f"workers: {decision.max_workers}")
        print(f"parallel requests: {decision.max_parallel_requests}")
        print(f"compile allowed: {'yes' if decision.compile_allowed else 'no'}")
        if decision.warning:
            print(f"warning: {decision.warning}")
        for reason in decision.reasons:
            print(f"reason: {reason}")
    return 0 if decision.allowed else 3
