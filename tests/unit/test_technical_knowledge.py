import json
from pathlib import Path

import pytest

from core.knowledge.catalog import KnowledgeCatalogError, load_language_catalog
from core.knowledge.models import KnowledgeEntry, KnowledgeKind, KnowledgeSource, KnowledgeStatus
from core.knowledge.registry import KnowledgeRegistry

ROOT = Path(__file__).parents[2]
LANGUAGE_CATALOG = ROOT / "knowledge/programming/languages/entries.json"
FRAMEWORK_CATALOG = ROOT / "knowledge/programming/frameworks/catalog.json"
SOURCE_CATALOG = ROOT / "knowledge/programming/sources.json"


def source() -> KnowledgeSource:
    return KnowledgeSource("official://language-spec", "specification", "1.0")


def test_validated_knowledge_requires_sources_and_verification() -> None:
    with pytest.raises(ValueError, match="sources and verification"):
        KnowledgeEntry(
            name="Java",
            kind=KnowledgeKind.LANGUAGE,
            summary="Java knowledge",
            status=KnowledgeStatus.VALIDATED,
            verification=("spec review",),
        )


def test_registry_rejects_duplicate_ids_and_names() -> None:
    registry = KnowledgeRegistry()
    first = KnowledgeEntry(
        name="Java",
        kind=KnowledgeKind.LANGUAGE,
        summary="JVM language",
        sources=(source(),),
        verification=("spec review",),
        status=KnowledgeStatus.VALIDATED,
    )
    registry.register(first)
    with pytest.raises(ValueError, match="id already registered"):
        registry.register(first)
    duplicate_name = KnowledgeEntry(
        name="JAVA",
        kind=KnowledgeKind.LANGUAGE,
        summary="Duplicate name",
        sources=(source(),),
        verification=("spec review",),
        status=KnowledgeStatus.VALIDATED,
    )
    with pytest.raises(ValueError, match="name already registered"):
        registry.register(duplicate_name)


def test_registry_selects_validated_entries_by_kind() -> None:
    registry = KnowledgeRegistry()
    registry.register(
        KnowledgeEntry(
            name="Python",
            kind=KnowledgeKind.LANGUAGE,
            summary="Language",
            sources=(source(),),
            verification=("spec review",),
            status=KnowledgeStatus.VALIDATED,
        )
    )
    registry.register(
        KnowledgeEntry(
            name="Django",
            kind=KnowledgeKind.FRAMEWORK,
            summary="Web framework",
            sources=(source(),),
            verification=("documentation review",),
            status=KnowledgeStatus.EXPERIMENTAL,
        )
    )
    assert [entry.name for entry in registry.validated(kind=KnowledgeKind.LANGUAGE)] == ["Python"]
    assert registry.validated(kind=KnowledgeKind.FRAMEWORK) == ()


def test_language_catalog_has_required_dimensions_and_java() -> None:
    data = json.loads(LANGUAGE_CATALOG.read_text())
    assert data["schema_version"] == "1.0"
    names = {entry["name"] for entry in data["entries"]}
    assert {"Python", "Java", "Rust", "Go", "JavaScript", "TypeScript"} <= names
    required = {
        "syntax", "semantics", "type_system", "memory_model", "concurrency", "runtime",
        "toolchain", "testing", "debugging", "security", "ecosystems",
    }
    for entry in data["entries"]:
        assert required <= set(entry["topics"])
        assert entry["status"] == "validated"
        assert entry["toolchain"]


def test_framework_catalog_covers_major_language_ecosystems() -> None:
    data = json.loads(FRAMEWORK_CATALOG.read_text())
    pairs = {(item["name"], item["language"]) for item in data["frameworks"]}
    assert ("Spring Boot", "Java") in pairs
    assert ("Django", "Python") in pairs
    assert ("Flutter", "Dart") in pairs
    assert ("Tokio", "Rust") in pairs
    assert ("ASP.NET Core", "C#") in pairs
    for item in data["frameworks"]:
        assert item["build_tools"]
        assert item["testing"]
        assert item["topics"]


def test_authoritative_sources_exist_for_validated_language_entries() -> None:
    languages = json.loads(LANGUAGE_CATALOG.read_text())["entries"]
    sources = json.loads(SOURCE_CATALOG.read_text())["sources"]
    source_names = {item["name"] for item in sources}
    required_sources = {
        "Python Language Reference", "Java SE Specifications", "Rust Reference",
        "Go Language Specification", "ECMAScript Specification", "TypeScript Handbook",
        "C# Language Reference", "Kotlin Documentation", "The Swift Programming Language",
        "Dart Language Tour",
    }
    assert required_sources <= source_names
    assert len(languages) >= 12
    assert all(item["status"] == "validated" for item in languages)


def test_language_catalog_loader_builds_validated_runtime_entries() -> None:
    registry = load_language_catalog(ROOT)
    assert len(registry.validated(kind=KnowledgeKind.LANGUAGE)) == 12
    java = registry.get_by_name("java")
    assert java.status is KnowledgeStatus.VALIDATED
    assert java.sources
    assert java.verification
    assert "Maven" in java.toolchains


def test_language_catalog_loader_rejects_missing_source_mapping(tmp_path: Path) -> None:
    languages = json.loads(LANGUAGE_CATALOG.read_text())
    languages["entries"][0]["name"] = "Unknown Language"
    source_data = SOURCE_CATALOG.read_text()
    lang_dir = tmp_path / "knowledge" / "programming" / "languages"
    lang_dir.mkdir(parents=True)
    (lang_dir / "entries.json").write_text(json.dumps(languages))
    (tmp_path / "knowledge" / "programming" / "sources.json").write_text(source_data)
    with pytest.raises(KnowledgeCatalogError, match="source mapping"):
        load_language_catalog(tmp_path)
