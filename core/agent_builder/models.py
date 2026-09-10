from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class DraftStatus(StrEnum):
    DRAFT = "draft"
    VALID = "valid"
    PUBLISHED = "published"
    ARCHIVED = "archived"


@dataclass(frozen=True, slots=True)
class AgentDraft:
    id: str
    name: str
    division: str
    description: str
    responsibilities: tuple[str, ...]
    deliverables: tuple[str, ...]
    success_criteria: tuple[str, ...]
    boundaries: tuple[str, ...]
    skills: tuple[str, ...] = ()
    capabilities: tuple[str, ...] = ()
    permissions: tuple[str, ...] = ()
    harnesses: tuple[str, ...] = ()
    environments: tuple[str, ...] = ()
    base_agent_id: str | None = None
    status: DraftStatus = DraftStatus.DRAFT
    revision: int = 1


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    agent: dict[str, object] | None = None
    markdown: str | None = None

    def as_dict(self) -> dict[str, object]:
        return {"valid": self.valid, "errors": list(self.errors), "warnings": list(self.warnings),
                "agent": self.agent, "markdown": self.markdown}


MAX_TEXT = 4000
MAX_ITEMS = 32
MAX_ID = 96


def validate_shape(draft: AgentDraft) -> tuple[str, ...]:
    errors: list[str] = []
    if not draft.id or draft.id != draft.id.strip() or len(draft.id) > MAX_ID:
        errors.append("id must be non-empty, trimmed, and at most 96 characters")
    if any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for c in draft.id):
        errors.append("id may contain only lowercase letters, digits, '-' and '_'")
    for field in ("name", "division", "description"):
        value = getattr(draft, field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{field} is required")
        elif len(value) > MAX_TEXT:
            errors.append(f"{field} exceeds {MAX_TEXT} characters")
    for field in ("responsibilities", "deliverables", "success_criteria", "boundaries", "skills", "capabilities", "permissions", "harnesses", "environments"):
        values = getattr(draft, field)
        if len(values) > MAX_ITEMS:
            errors.append(f"{field} exceeds {MAX_ITEMS} items")
        if len(values) != len(set(values)):
            errors.append(f"{field} contains duplicates")
        if any(not isinstance(x, str) or not x.strip() or len(x) > MAX_TEXT for x in values):
            errors.append(f"{field} contains an invalid item")
    if not draft.responsibilities:
        errors.append("responsibilities must not be empty")
    if not draft.deliverables:
        errors.append("deliverables must not be empty")
    if not draft.success_criteria:
        errors.append("success_criteria must not be empty")
    if not draft.boundaries:
        errors.append("boundaries must not be empty")
    if draft.revision < 1:
        errors.append("revision must be positive")
    return tuple(errors)
