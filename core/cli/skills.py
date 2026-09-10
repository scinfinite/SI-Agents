from __future__ import annotations

import json
from pathlib import Path

from core.skills.composer import compose
from core.skills.registry import SkillRegistry


def registry(root: Path) -> SkillRegistry:
    return SkillRegistry().load_directory(root / "skills") and _load(root)


def _load(root: Path) -> SkillRegistry:
    value = SkillRegistry()
    value.load_directory(root / "skills")
    return value


def list_skills(root: Path, *, category: str | None = None, status: str = "validated", search: str | None = None) -> tuple[dict[str, object], ...]:
    value = _load(root)
    return tuple(skill.as_dict() for skill in value.select(category=category, status=status, query=search))


def inspect_skill(root: Path, skill_id: str) -> dict[str, object]:
    return _load(root).get(skill_id).as_dict()


def compose_skills(root: Path, skill_ids: list[str]) -> dict[str, object]:
    value = _load(root)
    composition = compose([value.get(skill_id) for skill_id in skill_ids])
    return {
        "skills": list(composition.skills),
        "inputs": list(composition.inputs),
        "outputs": list(composition.outputs),
        "dependencies": list(composition.dependencies),
    }


def print_skills(root: Path, *, category: str | None, status: str, search: str | None, as_json: bool) -> int:
    payload = list_skills(root, category=category, status=status, search=search)
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for item in payload:
            print(f"{item['id']}: {item['name']} [{item['category']}, {item['version']}, {item['status']}]")
            print(f"  {item['purpose']}")
    return 0
