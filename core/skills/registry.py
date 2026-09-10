from __future__ import annotations

from core.skills.models import Skill, SkillStatus


class SkillRegistry:
    """Registry for reusable procedures; registration never grants execution permission."""

    def __init__(self) -> None:
        self._skills: dict[str, Skill] = {}

    def register(self, skill: Skill) -> Skill:
        if skill.id in self._skills:
            raise ValueError(f"Duplicate skill id: {skill.id}")
        if any(existing.name == skill.name for existing in self._skills.values()):
            raise ValueError(f"Duplicate skill name: {skill.name}")
        self._skills[skill.id] = skill
        return skill

    def get(self, skill_id: str) -> Skill:
        try:
            return self._skills[skill_id]
        except KeyError as exc:
            raise KeyError(f"Unknown skill: {skill_id}") from exc

    def all(self) -> tuple[Skill, ...]:
        return tuple(self._skills.values())

    def by_category(self, category: str) -> tuple[Skill, ...]:
        return tuple(skill for skill in self._skills.values() if skill.category == category)

    def by_status(self, status: SkillStatus) -> tuple[Skill, ...]:
        return tuple(skill for skill in self._skills.values() if skill.status is status)

    def select(
        self,
        *,
        category: str | None = None,
        required_tools: tuple[str, ...] = (),
        required_permissions: tuple[str, ...] = (),
        validated_only: bool = True,
    ) -> tuple[Skill, ...]:
        allowed = {SkillStatus.VALIDATED} if validated_only else {
            SkillStatus.EXPERIMENTAL, SkillStatus.VALIDATED
        }
        return tuple(
            skill
            for skill in self._skills.values()
            if skill.status in allowed
            and (category is None or skill.category == category)
            and set(required_tools).issubset(skill.required_tools)
            and set(required_permissions).issubset(skill.required_permissions)
        )
