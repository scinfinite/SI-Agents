from core.capabilities import Capability, CapabilityStatus, CapabilityStore, CapabilityRegistry


def test_capability_store_round_trip(tmp_path):
    path = tmp_path / "capabilities.json"
    registry = CapabilityRegistry()
    item = registry.register(
        Capability(
            name="debug",
            category="engineering",
            status=CapabilityStatus.VALIDATED,
            verification=("pytest",),
            tools=("pytest",),
            confidence=0.9,
            version="1.2.3",
        )
    )
    CapabilityStore(path).save(registry)
    restored = CapabilityRegistry()
    loaded = CapabilityStore(path).load(restored)
    assert loaded[0] == item
    assert restored.get_by_name("debug").version == "1.2.3"


def test_missing_store_is_empty(tmp_path):
    assert CapabilityStore(tmp_path / "missing.json").load(CapabilityRegistry()) == ()
