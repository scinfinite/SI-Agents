from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4


class CapabilityStatus(str, Enum):
    UNKNOWN = "unknown"
    EXPERIMENTAL = "experimental"
    VALIDATED = "validated"
    DEPRECATED = "deprecated"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class Capability:
    name: str
    category: str
    status: CapabilityStatus = CapabilityStatus.UNKNOWN
    agent: str | None = None
    skills: tuple[str, ...] = ()
    tools: tuple[str, ...] = ()
    permissions: tuple[str, ...] = ()
    inputs: tuple[str, ...] = ()
    outputs: tuple[str, ...] = ()
    verification: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    confidence: float | None = None
    version: str | None = None
    id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Capability name must not be empty")
        if not self.category.strip():
            raise ValueError("Capability category must not be empty")
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Capability confidence must be between 0 and 1")
        if self.status is CapabilityStatus.VALIDATED and not self.verification:
            raise ValueError("Validated capability must declare verification criteria")


class CapabilityRegistry:
    def __init__(self) -> None:
        self._capabilities: dict[str, Capability] = {}

    def register(self, capability: Capability) -> Capability:
        if capability.id in self._capabilities:
            raise ValueError(f"Capability ID already registered: {capability.id}")
        if any(item.name == capability.name for item in self._capabilities.values()):
            raise ValueError(f"Capability name already registered: {capability.name}")
        self._capabilities[capability.id] = capability
        return capability

    def get(self, capability_id: str) -> Capability:
        try:
            return self._capabilities[capability_id]
        except KeyError as exc:
            raise KeyError(f"Unknown capability: {capability_id}") from exc

    def all(self) -> tuple[Capability, ...]:
        return tuple(self._capabilities.values())

    def by_status(self, status: CapabilityStatus) -> tuple[Capability, ...]:
        return tuple(item for item in self._capabilities.values() if item.status is status)
