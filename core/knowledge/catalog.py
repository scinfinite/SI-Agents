from __future__ import annotations

import json
from pathlib import Path

from core.knowledge.models import KnowledgeEntry, KnowledgeKind, KnowledgeSource, KnowledgeStatus
from core.knowledge.registry import KnowledgeRegistry


class KnowledgeCatalogError(ValueError):
    """Raised when an on-disk knowledge catalog is malformed."""


def load_language_catalog(root: Path) -> KnowledgeRegistry:
    """Load the checked-in language catalog into the runtime registry."""
    path = root / "knowledge" / "programming" / "languages" / "entries.json"
    sources_path = root / "knowledge" / "programming" / "sources.json"
    try:
        entries_data = json.loads(path.read_text(encoding="utf-8"))
        sources_data = json.loads(sources_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise KnowledgeCatalogError(f"Unable to load knowledge catalog: {exc}") from exc

    source_by_name = {item["name"]: item for item in sources_data.get("sources", [])}
    registry = KnowledgeRegistry()
    for item in entries_data.get("entries", []):
        source_name = _source_for_language(item["name"])
        source = source_by_name.get(source_name)
        if source is None:
            raise KnowledgeCatalogError(f"Missing authoritative source for {item['name']}")
        entry = KnowledgeEntry(
            name=item["name"],
            kind=KnowledgeKind.LANGUAGE,
            summary=(
                f"{item['name']}: {item['family']}; execution={item['execution']}; "
                f"runtime={item['runtime']}"
            ),
            topics=tuple(item["topics"]),
            toolchains=tuple(item["toolchain"]),
            related=tuple(item["ecosystems"]),
            sources=(KnowledgeSource(source["url"], "authoritative-reference"),),
            status=KnowledgeStatus.VALIDATED,
            confidence=1.0,
            verification=("catalog-schema", "authoritative-source-record"),
        )
        registry.register(entry)
    return registry


def _source_for_language(name: str) -> str:
    mapping = {
        "Python": "Python Language Reference",
        "Java": "Java SE Specifications",
        "Rust": "Rust Reference",
        "Go": "Go Language Specification",
        "JavaScript": "ECMAScript Specification",
        "TypeScript": "TypeScript Handbook",
        "C": "C Standard",
        "C++": "C++ Reference",
        "C#": "C# Language Reference",
        "Kotlin": "Kotlin Documentation",
        "Swift": "The Swift Programming Language",
        "Dart": "Dart Language Tour",
        "SQL": "PostgreSQL Documentation",
    }
    try:
        return mapping[name]
    except KeyError as exc:
        raise KnowledgeCatalogError(f"No authoritative source mapping for {name}") from exc
