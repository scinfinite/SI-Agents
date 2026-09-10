import pytest

from core.capabilities.registry import Capability, CapabilityRegistry, CapabilityStatus


def test_registry_registers_and_filters_capabilities() -> None:
    registry = CapabilityRegistry()
    capability = registry.register(
        Capability(
            name="python-test",
            category="testing",
            status=CapabilityStatus.VALIDATED,
            verification=("pytest passes",),
            confidence=0.9,
        )
    )

    assert registry.get(capability.id) is capability
    assert registry.by_status(CapabilityStatus.VALIDATED) == (capability,)
    assert registry.all() == (capability,)


def test_registry_rejects_duplicate_names_and_ids() -> None:
    registry = CapabilityRegistry()
    first = registry.register(Capability(name="lint", category="quality"))

    with pytest.raises(ValueError, match="name already registered"):
        registry.register(Capability(name="lint", category="quality"))

    duplicate_id = Capability(name="format", category="quality", id=first.id)
    with pytest.raises(ValueError, match="ID already registered"):
        registry.register(duplicate_id)


def test_validated_capability_requires_verification() -> None:
    with pytest.raises(ValueError, match="verification criteria"):
        Capability(
            name="unsafe-validation",
            category="testing",
            status=CapabilityStatus.VALIDATED,
        )


def test_confidence_is_bounded() -> None:
    with pytest.raises(ValueError, match="between 0 and 1"):
        Capability(name="bad-confidence", category="testing", confidence=1.1)
