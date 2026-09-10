from __future__ import annotations

from pathlib import Path

from core.skills.models import Skill
from core.skills.parser import parse_skill_file
from core.skills.validator import require_valid


class SkillRegistry:
    """Deterministic registry; loading or selecting a Skill never grants authority."""

    def __init__(self) -> None:
        self._skills: dict[str, Skill] = {}

    def register(self, skill: Skill) -> Skill:
        require_valid(skill)
        if skill.id in self._skills:
            raise ValueError(f"Duplicate skill id: {skill.id}")
        if any(item.name == skill.name for item in self._skills.values()):
            raise ValueError(f"Duplicate skill name: {skill.name}")
        self._skills[skill.id] = skill
        return skill

    def get(self, skill_id: str) -> Skill:
        try:
            return self._skills[skill_id]
        except KeyError as exc:
            raise KeyError(f"Unknown skill: {skill_id}") from exc

    def all(self) -> tuple[Skill, ...]:
        return tuple(sorted(self._skills.values(), key=lambda item: item.id))

    def load_directory(self, root: str | Path) -> tuple[Skill, ...]:
        root = Path(root)
        if not root.is_dir():
            raise FileNotFoundError(f"Skill directory not found: {root}")
        for path in sorted(root.rglob("SKILL.md")):
            self.register(parse_skill_file(path))
        return self.all()

    def select(self, *, category: str | None = None, status: str = "validated", query: str | None = None) -> tuple[Skill, ...]:
        needle = query.casefold() if query else None
        return tuple(
            skill for skill in self.all()
            if skill.status.value == status
            and (category is None or skill.category == category)
            and (needle is None or needle in (skill.id + " " + skill.name + " " + skill.purpose).casefold())
        )
