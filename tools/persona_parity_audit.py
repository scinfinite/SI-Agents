"""Audit the checked-in SI persona corpus for deterministic Phase 29 invariants."""
from __future__ import annotations

import json
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DANGEROUS = {"Cf"}


def main() -> int:
    paths = sorted(p for p in (ROOT / "agents").rglob("*.md") if p.name != "README.md")
    index = json.loads((ROOT / "config/persona-source-index.json").read_text(encoding="utf-8"))
    catalog = json.loads((ROOT / "config/agent-catalog.json").read_text(encoding="utf-8"))
    if len(paths) != 279 or index["agent_count"] != 279 or len(index["agents"]) != 279 or len(catalog["agents"]) != 279:
        raise SystemExit("persona parity count failure")
    ids = {item["id"] for item in index["agents"]}
    if len(ids) != 279 or len({item["source_path"] for item in index["agents"]}) != 279:
        raise SystemExit("persona parity identity failure")
    for path in paths:
        text = path.read_text(encoding="utf-8")
        if any(unicodedata.category(char) in DANGEROUS for char in text):
            raise SystemExit(f"hidden Unicode control character: {path}")
        if not text.startswith("---\n"):
            raise SystemExit(f"invalid persona frontmatter: {path}")
    print("PHASE 29 PERSONA PARITY PASS: 279 personas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
