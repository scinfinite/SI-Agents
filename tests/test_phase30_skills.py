from __future__ import annotations

import pytest
from pathlib import Path

from core.skills.artifacts import build_manifest, load_artifact
from core.skills.composer import compose
from core.skills.models import Skill, SkillRequirement, SkillStatus
from core.skills.parser import parse_skill
from core.skills.registry import SkillRegistry
from core.skills.validator import validate_skill

ROOT = Path(__file__).resolve().parents[1]


def test_all_canonical_skills_parse_and_validate() -> None:
    registry = SkillRegistry()
    skills = registry.load_directory(ROOT / "skills")
    assert len(skills) == 6
    assert all(not validate_skill(skill) for skill in skills)
    assert [skill.id for skill in skills] == sorted(skill.id for skill in skills)


def test_parser_rejects_authority_fields() -> None:
    source = "---\nschema: si-agents.skill.v1\nversion: 1.0\nid: unsafe\nname: Unsafe\ncategory: test\nstatus: validated\npermissions: root\n---\n"
    with pytest.raises(ValueError, match="privilege"):
        parse_skill(source)


def test_parser_rejects_malformed_sections() -> None:
    source = "---\nschema: si-agents.skill.v1\nversion: 1.0\nid: bad\nname: Bad\ncategory: test\nstatus: validated\n---\n## Purpose\nonly purpose\n"
    with pytest.raises(ValueError, match="sections missing"):
        parse_skill(source)


def test_skill_selection_is_deterministic() -> None:
    registry = SkillRegistry()
    registry.load_directory(ROOT / "skills")
    result = registry.select(category="engineering", query="repository")
    assert [item.id for item in result] == ["inspect-repository"]


def test_composition_resolves_dependencies() -> None:
    registry = SkillRegistry()
    registry.load_directory(ROOT / "skills")
    selected = [registry.get("compose-workflow"), registry.get("inspect-repository"), registry.get("verify-change")]
    composition = compose(selected)
    assert composition.skills[-1] == "compose-workflow"
    assert set(composition.skills) == {skill.id for skill in selected}
    assert "inspect-repository" in composition.dependencies


def test_composition_rejects_missing_dependency() -> None:
    registry = SkillRegistry()
    registry.load_directory(ROOT / "skills")
    with pytest.raises(ValueError, match="missing dependencies"):
        compose([registry.get("compose-workflow")])


def test_composition_rejects_cycles() -> None:
    def make(identifier: str, dependencies: tuple[str, ...]) -> Skill:
        return Skill(
            "si-agents.skill.v1", "1.0", identifier, identifier, "test", "purpose",
            ("input",), ("output",), ("precondition",), ("step",), ("tool",),
            ("filesystem_read",), ("repository_read",), ("check",), ("stop",),
            ("evidence",), ("example",), (SkillRequirement("si-core", "runtime", "1.x")),
            "SI-native test provenance", SkillStatus.VALIDATED, dependencies,
        )
    with pytest.raises(ValueError, match="cyclic"):
        compose([make("a", ("b",)), make("b", ("a",))])


def test_artifact_digest_is_stable() -> None:
    path = ROOT / "skills" / "engineering" / "inspect-repository" / "SKILL.md"
    first = load_artifact(path)
    second = load_artifact(path)
    assert first.sha256 == second.sha256
    manifest = build_manifest((first,))
    assert manifest["schema"] == "si-agents.skill-manifest.v1"
    assert manifest["skills"][0]["sha256"] == first.sha256
