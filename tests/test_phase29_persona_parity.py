from __future__ import annotations

import json
from pathlib import Path

from core.organization.loader import load_catalog
from core.personas.registry import PersonaRegistry

ROOT = Path(__file__).resolve().parents[1]


def test_phase29_has_current_300_personas() -> None:
    paths = sorted(p for p in (ROOT / "agents").rglob("*.md") if p.name != "README.md")
    assert len(paths) == 300
    assert all(p.read_text(encoding="utf-8").startswith("---\n") for p in paths)


def test_phase29_provenance_manifest_is_complete() -> None:
    data = json.loads((ROOT / "config/persona-source-index.json").read_text(encoding="utf-8"))
    assert data["agent_count"] == 300
    assert data["source_division_count"] == 18
    assert len(data["snapshot"]) == 40
    assert "repository" not in data


def test_persona_registry_and_catalog_match() -> None:
    registry = PersonaRegistry()
    loaded = registry.load_directory(ROOT / "agents")
    assert len(loaded) == 300
    catalog = load_catalog(ROOT / "config/agent-catalog.json")
    assert len(catalog.all()) == 300
    by_id = {agent.id: agent for agent in catalog.all()}
    assert len(by_id) == 300
    assert registry.validate_against_catalog(catalog) == ()


def test_personas_contain_no_hidden_unicode_controls() -> None:
    dangerous = {"\u202a", "\u202b", "\u202c", "\u202d", "\u202e", "\u2066", "\u2067", "\u2068", "\u2069", "\u200b", "\u200c", "\u200d", "\ufeff"}
    for path in (ROOT / "agents").rglob("*.md"):
        if path.name == "README.md":
            continue
        text = path.read_text(encoding="utf-8")
        assert not dangerous.intersection(text), path
