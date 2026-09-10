from __future__ import annotations

import json
from pathlib import Path

from core.personas.registry import PersonaRegistry

ROOT = Path(__file__).resolve().parents[1]


def test_phase29_has_exactly_279_personas() -> None:
    paths = sorted(p for p in (ROOT / "agents").rglob("*.md") if p.name != "README.md")
    assert len(paths) == 279
    assert all(p.read_text(encoding="utf-8").startswith("---\n") for p in paths)


def test_phase29_source_index_is_one_to_one() -> None:
    data = json.loads((ROOT / "config/persona-source-index.json").read_text(encoding="utf-8"))
    assert data["agent_count"] == 279
    entries = data["agents"]
    assert len(entries) == 279
    assert len({entry["id"] for entry in entries}) == 279
    assert len({entry["source_path"] for entry in entries}) == 279
    assert all(len(entry["source_sha"]) == 40 for entry in entries)


def test_phase29_registry_and_catalog_match() -> None:
    registry = PersonaRegistry()
    loaded = registry.load_directory(ROOT / "agents")
    assert len(loaded) == 279
    catalog = json.loads((ROOT / "config/agent-catalog.json").read_text(encoding="utf-8"))
    assert len(catalog["agents"]) == 279
    by_id = {agent["id"]: agent for agent in catalog["agents"]}
    assert len(by_id) == 279
    assert registry.validate_against_catalog(_CatalogAdapter(by_id)) == ()


def test_phase29_personas_contain_no_hidden_unicode_controls() -> None:
    dangerous = {"\u202a", "\u202b", "\u202c", "\u202d", "\u202e", "\u2066", "\u2067", "\u2068", "\u2069", "\u200b", "\u200c", "\u200d", "\ufeff"}
    for path in (ROOT / "agents").rglob("*.md"):
        if path.name == "README.md":
            continue
        text = path.read_text(encoding="utf-8")
        assert not dangerous.intersection(text), path


class _CatalogAdapter:
    def __init__(self, values: dict[str, dict[str, object]]) -> None:
        self.values = values

    def get(self, key: str):
        value = self.values[key]
        return type("CatalogAgent", (), {"name": value["name"], "division": value["division"]})()
