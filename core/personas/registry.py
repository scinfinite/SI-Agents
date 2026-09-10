from __future__ import annotations

from pathlib import Path

from core.personas.models import AgentPersona
from core.personas.parser import parse_persona_file
from core.personas.validator import validate_persona


class PersonaRegistry:
    """Deterministic registry of human-authored personas, separate from privileges."""

    def __init__(self) -> None:
        self._personas: dict[str, AgentPersona] = {}

    def register(self, persona: AgentPersona) -> AgentPersona:
        errors = validate_persona(persona)
        if errors:
            raise ValueError("Invalid persona: " + "; ".join(errors))
        existing = self._personas.get(persona.id)
        if existing is not None:
            raise ValueError(f"Duplicate persona id: {persona.id}")
        if any(item.name == persona.name for item in self._personas.values()):
            raise ValueError(f"Duplicate persona name: {persona.name}")
        self._personas[persona.id] = persona
        return persona

    def load_directory(self, directory: str | Path) -> tuple[AgentPersona, ...]:
        root = Path(directory)
        if not root.is_dir():
            raise ValueError(f"Persona directory does not exist: {root}")
        paths = sorted(root.rglob("*.md"))
        loaded = tuple(parse_persona_file(path) for path in paths)
        for persona in loaded:
            self.register(persona)
        return loaded

    def get(self, persona_id: str) -> AgentPersona:
        try:
            return self._personas[persona_id]
        except KeyError as exc:
            raise KeyError(f"Unknown persona: {persona_id}") from exc

    def all(self) -> tuple[AgentPersona, ...]:
        return tuple(self._personas.values())

    def validate_against_catalog(self, catalog: object) -> tuple[str, ...]:
        errors: list[str] = []
        for persona in self._personas.values():
            try:
                agent = catalog.get(persona.id)
            except KeyError:
                errors.append(f"persona {persona.id} is absent from agent catalog")
                continue
            if agent.name != persona.name:
                errors.append(f"persona {persona.id} name conflicts with agent catalog")
            if agent.division != persona.division:
                errors.append(f"persona {persona.id} division conflicts with agent catalog")
        return tuple(errors)
