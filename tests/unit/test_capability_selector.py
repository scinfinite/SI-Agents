from core.capabilities.registry import Capability, CapabilityRegistry, CapabilityStatus
from core.orchestrator.capability_selector import CapabilitySelector


def test_selector_requires_validated_capabilities_by_default() -> None:
    registry = CapabilityRegistry()
    registry.register(
        Capability(
            name="validated-test",
            category="testing",
            status=CapabilityStatus.VALIDATED,
            tools=("pytest",),
            permissions=("execute:tests",),
            verification=("pytest passes",),
        )
    )
    registry.register(
        Capability(
            name="experimental-test",
            category="testing",
            status=CapabilityStatus.EXPERIMENTAL,
            tools=("pytest",),
            permissions=("execute:tests",),
        )
    )

    selected = CapabilitySelector(registry).select(
        category="testing",
        required_tools=("pytest",),
        required_permissions=("execute:tests",),
    )

    assert [item.name for item in selected] == ["validated-test"]


def test_selector_can_include_experimental_capabilities() -> None:
    registry = CapabilityRegistry()
    registry.register(
        Capability(
            name="experimental-test",
            category="testing",
            status=CapabilityStatus.EXPERIMENTAL,
        )
    )

    selected = CapabilitySelector(registry).select(category="testing", validated_only=False)

    assert [item.name for item in selected] == ["experimental-test"]
