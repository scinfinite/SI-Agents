from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class AgentPersona:
    """Human-authored behavioral definition; never an authority for privileges."""

    schema: str
    version: int
    id: str
    name: str
    division: str
    description: str
    identity: str
    personality: str
    mission: str
    expertise: tuple[str, ...]
    responsibilities: tuple[str, ...]
    workflow: tuple[str, ...]
    critical_rules: tuple[str, ...]
    boundaries: tuple[str, ...]
    deliverables: tuple[str, ...]
    failure_behavior: tuple[str, ...]
    escalation_behavior: tuple[str, ...]
    verification_expectations: tuple[str, ...]
    evidence_requirements: tuple[str, ...]
    source_path: str | None = None

    def __post_init__(self) -> None:
        if self.schema != "si-agents.agent-persona.v1":
            raise ValueError(f"Unsupported persona schema: {self.schema!r}")
        if self.version != 1:
            raise ValueError(f"Unsupported persona version: {self.version!r}")
        _require_id(self.id)
        for name in ("name", "division", "description", "identity", "personality", "mission"):
            if not getattr(self, name).strip():
                raise ValueError(f"Persona {self.id} requires {name}")
        for name in _LIST_FIELDS:
            values = getattr(self, name)
            if not values or any(not item.strip() for item in values):
                raise ValueError(f"Persona {self.id} requires non-empty {name}")
        if self.source_path is not None:
            Path(self.source_path)

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-safe representation without granting any authority."""
        return asdict(self)


_LIST_FIELDS = (
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
)


def _require_id(value: str) -> None:
    if not value or value != value.strip() or any(
        char not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for char in value
    ):
        raise ValueError(f"Invalid persona id: {value!r}")
