from __future__ import annotations

from dataclasses import replace

from core.organization.models import AgentDefinition
from core.personas.models import AgentPersona
from core.personas.validator import validate_persona


def compile_persona(persona: AgentPersona, base: AgentDefinition) -> AgentDefinition:
    """Merge human behavioral fields into an existing typed contract.

    Governance fields on ``AgentDefinition`` are authoritative and are copied
    unchanged. A persona can therefore describe behavior but cannot grant a
    capability, permission, harness, environment, or executable implementation.
    """
    errors = validate_persona(persona)
    if errors:
        raise ValueError("Invalid persona: " + "; ".join(errors))
    if persona.id != base.id:
        raise ValueError(f"Persona identity mismatch: {persona.id} != {base.id}")
    if persona.name != base.name:
        raise ValueError(f"Persona name mismatch for {base.id}")
    if persona.division != base.division:
        raise ValueError(f"Persona division mismatch for {base.id}")
    return replace(
        base,
        description=persona.description,
        responsibilities=persona.responsibilities,
        deliverables=persona.deliverables,
        boundaries=persona.boundaries,
    )
