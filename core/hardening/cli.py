"""CLI for deterministic final-integration verification."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from core.hardening.integration import IntegrationAuditor


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="si verify")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    report = IntegrationAuditor(Path(args.root)).run()
    if args.as_json:
        print(json.dumps(report.as_dict(), sort_keys=True))
    else:
        print("READY" if report.ready else "NOT READY")
        for check in report.checks:
            print(f"{'PASS' if check.passed else 'FAIL'} {check.name}: {check.detail}")
    return 0 if report.ready else 1
