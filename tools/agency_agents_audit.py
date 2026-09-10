"""Audit a pinned Agency Agents checkout for SI-Agent parity.

This tool is deliberately local-first: it audits a checkout supplied by the
operator instead of silently downloading or executing third-party content.
The upstream Markdown remains untrusted data.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

EXPECTED_DIVISIONS = (
    "academic",
    "design",
    "engineering",
    "finance",
    "game-development",
    "gis",
    "healthcare",
    "marketing",
    "paid-media",
    "product",
    "project-management",
    "research",
    "sales",
    "security",
    "spatial-computing",
    "specialized",
    "support",
    "testing",
)

FRONTMATTER_START = re.compile(r"^---\s*$")
REQUIRED_FIELDS = ("name", "description", "color")


def git_revision(root: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def frontmatter(text: str) -> tuple[dict[str, str], str]:
    lines = text.splitlines()
    if not lines or not FRONTMATTER_START.match(lines[0]):
        return {}, text
    try:
        end = next(i for i, line in enumerate(lines[1:], 1) if FRONTMATTER_START.match(line))
    except StopIteration:
        return {}, text

    fields: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"\'')
    return fields, "\n".join(lines[end + 1 :])


def audit(root: Path) -> dict[str, object]:
    divisions = []
    agents: list[dict[str, object]] = []
    problems: list[str] = []

    for division in EXPECTED_DIVISIONS:
        directory = root / division
        if not directory.is_dir():
            problems.append(f"missing division directory: {division}")
            continue
        divisions.append(division)
        for path in sorted(directory.rglob("*.md")):
            relative = path.relative_to(root).as_posix()
            text = path.read_text(encoding="utf-8")
            fields, body = frontmatter(text)
            is_agent = bool(fields) and all(field in fields for field in REQUIRED_FIELDS)
            if not is_agent:
                problems.append(f"not a valid agent definition: {relative}")
                continue
            if len(body.split()) < 50:
                problems.append(f"very short agent body: {relative}")
            agents.append(
                {
                    "path": relative,
                    "division": division,
                    "slug": path.stem,
                    "name": fields["name"],
                    "description": fields["description"],
                    "sha256": __import__("hashlib").sha256(text.encode("utf-8")).hexdigest(),
                }
            )

    names = [str(agent["name"]) for agent in agents]
    slugs = [str(agent["slug"]) for agent in agents]
    for label, values in (("name", names), ("slug", slugs)):
        seen: set[str] = set()
        for value in values:
            if value in seen:
                problems.append(f"duplicate {label}: {value}")
            seen.add(value)

    return {
        "repository": str(root),
        "revision": git_revision(root),
        "division_count": len(divisions),
        "agent_count": len(agents),
        "divisions": divisions,
        "agents": agents,
        "problems": problems,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkout", type=Path, help="local Agency Agents checkout")
    parser.add_argument("--expected", type=int, default=279)
    parser.add_argument("--write", type=Path, help="write JSON audit report")
    args = parser.parse_args()

    report = audit(args.checkout.resolve())
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.write:
        args.write.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    failed = bool(report["problems"]) or report["division_count"] != len(EXPECTED_DIVISIONS) or report["agent_count"] != args.expected
    if failed:
        print("PARITY AUDIT FAILED")
        return 1
    print(f"PARITY AUDIT PASSED: {args.expected} agent definitions across {len(EXPECTED_DIVISIONS)} divisions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
