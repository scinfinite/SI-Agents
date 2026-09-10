from __future__ import annotations

from core.skills.models import Skill


class SkillValidationError(ValueError):
    pass


def validate_skill(skill: Skill) -> tuple[str, ...]:
    errors: list[str] = []
    if skill.id != skill.id.casefold():
        errors.append("skill id must be lowercase")
    if not skill.provenance.strip():
        errors.append("provenance is required")
    if any("grant" in item.casefold() or "bypass" in item.casefold() for item in skill.requested_permissions):
        errors.append("skills cannot grant or bypass permissions")
    if any("credential" in item.casefold() or "secret" in item.casefold() for item in skill.evidence_requirements):
        errors.append("evidence requirements cannot request credentials or secrets")
    if any(not requirement.name.strip() or not requirement.kind.strip() for requirement in skill.compatibility):
        errors.append("compatibility requirements must be complete")
    return tuple(errors)


def require_valid(skill: Skill) -> Skill:
    errors = validate_skill(skill)
    if errors:
        raise SkillValidationError("; ".join(errors))
    return skill
