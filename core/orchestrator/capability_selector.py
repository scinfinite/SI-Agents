from core.capabilities.registry import Capability, CapabilityRegistry, CapabilityStatus


class CapabilitySelector:
    """Select only capabilities that satisfy explicit execution requirements."""

    def __init__(self, registry: CapabilityRegistry) -> None:
        self.registry = registry

    def select(
        self,
        *,
        category: str,
        required_tools: tuple[str, ...] = (),
        required_permissions: tuple[str, ...] = (),
        validated_only: bool = True,
    ) -> tuple[Capability, ...]:
        if not category.strip():
            raise ValueError("Capability category must not be empty")

        candidates = self.registry.all()
        if validated_only:
            candidates = tuple(item for item in candidates if item.status is CapabilityStatus.VALIDATED)

        return tuple(
            item
            for item in candidates
            if item.category == category
            and all(tool in item.tools for tool in required_tools)
            and all(permission in item.permissions for permission in required_permissions)
        )
