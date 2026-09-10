from dataclasses import dataclass, field
from datetime import UTC, datetime

from core.capabilities.models import CapabilityStatus
from core.capabilities.registry import CapabilityRegistry


@dataclass(frozen=True)
class CapabilityDiscovery:
    name: str
    category: str
    source: str
    discovered_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        for value, label in ((self.name, "name"), (self.category, "category"), (self.source, "source")):
            if not value.strip():
                raise ValueError(f"Discovery {label} must not be empty")


class CapabilityDiscoveryIndex:
    """Tracks discovered candidates separately from executable capabilities."""

    def __init__(self) -> None:
        self._items: dict[str, CapabilityDiscovery] = {}

    def record(self, discovery: CapabilityDiscovery) -> CapabilityDiscovery:
        if discovery.name in self._items:
            raise ValueError(f"Capability discovery already exists: {discovery.name}")
        self._items[discovery.name] = discovery
        return discovery

    def get(self, name: str) -> CapabilityDiscovery:
        try:
            return self._items[name]
        except KeyError as exc:
            raise KeyError(f"Unknown discovered capability: {name}") from exc

    def all(self) -> tuple[CapabilityDiscovery, ...]:
        return tuple(self._items.values())

    def candidates_for_registration(self, registry: CapabilityRegistry) -> tuple[CapabilityDiscovery, ...]:
        known = {item.name for item in registry.all() if item.status is not CapabilityStatus.BLOCKED}
        return tuple(item for item in self._items.values() if item.name not in known)
