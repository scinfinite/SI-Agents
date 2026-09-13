"""Audit the checked-in SI persona corpus for deterministic invariants."""
from __future__ import annotations

import json
import unicodedata
from pathlib import Path

from core.organization import load_catalog

ROOT = Path(__file__).resolve().parents[1]
DANGEROUS = {"Cf"}


def main() -> int:
    paths = sorted(p for p in (ROOT / "agents").rglob("*.md") if p.name != "README.md")
    index = json.loads((ROOT / "config/persona-source-index.json").read_text(encoding="utf-8"))
    catalog = load_catalog(ROOT / "config/agent-catalog.json")
    if len(paths) != 300 or index["agent_count"] != 300 or index["source_division_count"] != 18 or len(catalog.all()) != 300:
        raise SystemExit("persona parity count failure")
    if len(index["snapshot"]) != 40 or "repository" in index:
        raise SystemExit("repository-neutral provenance failure")
    ids = [agent.id for agent in catalog.all()]
    if len(set(ids)) != 300:
        raise SystemExit("persona parity identity failure")
    for path in paths:
        text = path.read_text(encoding="utf-8")
        if any(unicodedata.category(char) in DANGEROUS for char in text):
            raise SystemExit(f"hidden Unicode control character: {path}")
        if not text.startswith("---\n"):
            raise SystemExit(f"invalid persona frontmatter: {path}")
    print("PERSONA PARITY PASS: 300 personas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
