from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from core.skills.models import Skill
from core.skills.parser import parse_skill_file
from core.skills.validator import validate_skill


@dataclass(frozen=True)
class SkillArtifact:
    skill: Skill
    sha256: str
    source_path: str


def load_artifact(path: str | Path) -> SkillArtifact:
    path = Path(path)
    raw = path.read_bytes()
    skill = parse_skill_file(path)
    errors = validate_skill(skill)
    if errors:
        raise ValueError("invalid Skill: " + "; ".join(errors))
    return SkillArtifact(skill, hashlib.sha256(raw).hexdigest(), str(path))


def build_manifest(artifacts: tuple[SkillArtifact, ...]) -> dict[str, object]:
    return {
        "schema": "si-agents.skill-manifest.v1",
        "skills": [
            {"id": item.skill.id, "version": item.skill.version, "sha256": item.sha256, "source": item.source_path}
            for item in sorted(artifacts, key=lambda item: item.skill.id)
        ],
    }


def manifest_json(artifacts: tuple[SkillArtifact, ...]) -> str:
    return json.dumps(build_manifest(artifacts), indent=2, sort_keys=True) + "\n"
