import time

import pytest

from core.capabilities import (
    Capability,
    CapabilityBenchmark,
    CapabilityBenchmarkStore,
    CapabilityDiscovery,
    CapabilityDiscoveryIndex,
    CapabilityHealthTracker,
    CapabilityLifecycle,
    CapabilityRegistry,
    CapabilityStatus,
    CapabilityVersionManager,
    bump_version,
    validate_version,
)
from core.orchestrator.capability_selector import CapabilitySelector


def capability(name="debug", status=CapabilityStatus.VALIDATED, **kwargs):
    return Capability(name=name, category="engineering", status=status, verification=("test",) if status is CapabilityStatus.VALIDATED else (), **kwargs)


def test_registry_indexes_name_category_and_replacement():
    registry = CapabilityRegistry()
    item = registry.register(capability(tools=("pytest",), confidence=0.8))
    assert registry.get_by_name("debug") is item
    assert registry.by_category("engineering") == (item,)
    updated = Capability(**{**item.__dict__, "name": "debug-v2", "version": "1.0.0"})
    assert registry.replace(updated) is updated
    assert registry.get_by_name("debug-v2") is updated


def test_selector_ranks_by_confidence_health_and_benchmark():
    registry = CapabilityRegistry()
    registry.register(capability("slow", confidence=0.5, health=1.0, benchmark_score=0.5))
    registry.register(capability("best", confidence=1.0, health=1.0, benchmark_score=1.0))
    matches = CapabilitySelector(registry).rank(category="engineering")
    assert matches[0].capability.name == "best"
    assert matches[0].score == 1.0


def test_selector_excludes_blocked_deprecated_and_unknown_by_default():
    registry = CapabilityRegistry()
    registry.register(capability("valid"))
    registry.register(capability("experimental", CapabilityStatus.EXPERIMENTAL))
    registry.register(capability("blocked", CapabilityStatus.BLOCKED))
    assert [item.name for item in CapabilitySelector(registry).select(category="engineering")] == ["valid"]
    assert {item.name for item in CapabilitySelector(registry).select(category="engineering", validated_only=False)} == {"valid", "experimental"}


def test_health_tracker_validates_range_and_unknown_capability():
    registry = CapabilityRegistry()
    item = registry.register(capability())
    tracker = CapabilityHealthTracker(registry)
    check = tracker.record(item.id, score=0.9, reason="smoke test")
    assert check.healthy is True
    with pytest.raises(ValueError):
        tracker.record(item.id, score=1.1)
    with pytest.raises(KeyError):
        tracker.record("missing", score=0.5)


def test_benchmark_store_tracks_latest():
    store = CapabilityBenchmarkStore()
    first = store.record(CapabilityBenchmark("cap", 0.5, "suite", False))
    time.sleep(0.001)
    second = store.record(CapabilityBenchmark("cap", 1.0, "suite", True))
    assert store.for_capability("cap") == (first, second)
    assert store.latest("cap") is second


def test_lifecycle_requires_evidence_for_validation_and_blocks_safely():
    registry = CapabilityRegistry()
    item = registry.register(capability("candidate", CapabilityStatus.EXPERIMENTAL))
    lifecycle = CapabilityLifecycle(registry)
    with pytest.raises(ValueError):
        lifecycle.promote(item.id, verification=("test",), evidence=(), confidence=0.9)
    promoted = lifecycle.promote(item.id, verification=("test",), evidence=("ci:1",), confidence=0.9)
    assert promoted.status is CapabilityStatus.VALIDATED
    blocked = lifecycle.block(item.id, reason="security failure")
    assert blocked.status is CapabilityStatus.BLOCKED
    assert blocked.health == 0.0
    with pytest.raises(ValueError):
        lifecycle.promote(item.id, verification=("test",), evidence=("ci:2",), confidence=1.0)


def test_version_manager_and_validation():
    assert validate_version("1.2.3") == "1.2.3"
    assert bump_version("1.2.3", part="major") == "2.0.0"
    assert bump_version("1.2.3", part="minor") == "1.3.0"
    assert bump_version("1.2.3", part="patch") == "1.2.4"
    with pytest.raises(ValueError):
        validate_version("1.2")
    registry = CapabilityRegistry()
    item = registry.register(capability(version="1.0.0"))
    manager = CapabilityVersionManager(registry)
    assert manager.bump(item.id, part="minor").version == "1.1.0"


def test_discovery_is_not_execution_registration():
    registry = CapabilityRegistry()
    registry.register(capability("known"))
    index = CapabilityDiscoveryIndex()
    index.record(CapabilityDiscovery("known", "engineering", "scanner"))
    index.record(CapabilityDiscovery("new", "engineering", "scanner"))
    assert [item.name for item in index.candidates_for_registration(registry)] == ["new"]
