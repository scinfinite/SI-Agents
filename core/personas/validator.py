from __future__ import annotations

from core.personas.models import AgentPersona


def validate_persona(persona: AgentPersona) -> tuple[str, ...]:
    """Return deterministic semantic validation errors without mutating the persona."""
    errors: list[str] = []
    if persona.id != persona.id.lower():
        errors.append("persona id must be lowercase")
    if persona.name.strip() == "":
        errors.append("persona name is empty")
    if persona.division.strip() == "":
        errors.append("persona division is empty")
    for field in (
        "expertise",
        "responsibilities",
        "workflow",
        "critical_rules",
        "boundaries",
        "deliverables",
        "failure_behavior",
        "escalation_behavior",
        "verification_expectations",
        "evidence_requirements",
    ):
        values = getattr(persona, field)
        if len(values) != len(set(values)):
            errors.append(f"persona has duplicate {field}")
    return tuple(errors)
