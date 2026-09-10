from core.capabilities.models import Capability, CapabilityStatus


class CapabilityRegistry:
    """In-memory capability catalog with identity and state invariants."""

    def __init__(self) -> None:
        self._capabilities: dict[str, Capability] = {}
        self._names: dict[str, str] = {}

    def register(self, capability: Capability) -> Capability:
        if capability.id in self._capabilities:
            raise ValueError(f"Capability ID already registered: {capability.id}")
        if capability.name in self._names:
            raise ValueError(f"Capability name already registered: {capability.name}")
        self._capabilities[capability.id] = capability
        self._names[capability.name] = capability.id
        return capability

    def get(self, capability_id: str) -> Capability:
        try:
            return self._capabilities[capability_id]
        except KeyError as exc:
            raise KeyError(f"Unknown capability: {capability_id}") from exc

    def get_by_name(self, name: str) -> Capability:
        try:
            return self._capabilities[self._names[name]]
        except KeyError as exc:
            raise KeyError(f"Unknown capability name: {name}") from exc

    def all(self) -> tuple[Capability, ...]:
        return tuple(self._capabilities.values())

    def by_status(self, status: CapabilityStatus) -> tuple[Capability, ...]:
        return tuple(item for item in self._capabilities.values() if item.status is status)

    def by_category(self, category: str) -> tuple[Capability, ...]:
        return tuple(item for item in self._capabilities.values() if item.category == category)

    def replace(self, capability: Capability) -> Capability:
        current = self.get(capability.id)
        if capability.name != current.name and capability.name in self._names:
            raise ValueError(f"Capability name already registered: {capability.name}")
        if capability.name != current.name:
            del self._names[current.name]
            self._names[capability.name] = capability.id
        self._capabilities[capability.id] = capability
        return capability

    def update_status(self, capability_id: str, status: CapabilityStatus) -> Capability:
        current = self.get(capability_id)
        return self.replace(Capability(**{**current.__dict__, "status": status}))
