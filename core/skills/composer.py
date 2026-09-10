from __future__ import annotations

from dataclasses import dataclass

from core.skills.models import Skill


@dataclass(frozen=True)
class SkillComposition:
    skills: tuple[str, ...]
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    dependencies: tuple[str, ...]


def compose(skills: tuple[Skill, ...] | list[Skill]) -> SkillComposition:
    selected = {skill.id: skill for skill in skills}
    if len(selected) != len(skills):
        raise ValueError("composition contains duplicate Skill IDs")
    missing = sorted({dep for skill in selected.values() for dep in skill.dependencies if dep not in selected})
    if missing:
        raise ValueError("composition has missing dependencies: " + ", ".join(missing))

    visiting: set[str] = set()
    visited: set[str] = set()
    ordered: list[Skill] = []

    def visit(skill_id: str) -> None:
        if skill_id in visiting:
            raise ValueError(f"cyclic Skill dependency: {skill_id}")
        if skill_id in visited:
            return
        visiting.add(skill_id)
        for dep in sorted(selected[skill_id].dependencies):
            visit(dep)
        visiting.remove(skill_id)
        visited.add(skill_id)
        ordered.append(selected[skill_id])

    for skill_id in sorted(selected):
        visit(skill_id)
    inputs = tuple(dict.fromkeys(item for skill in ordered for item in skill.inputs))
    outputs = tuple(dict.fromkeys(item for skill in ordered for item in skill.outputs))
    dependencies = tuple(dict.fromkeys(item for skill in ordered for item in skill.dependencies))
    return SkillComposition(tuple(skill.id for skill in ordered), inputs, outputs, dependencies)
