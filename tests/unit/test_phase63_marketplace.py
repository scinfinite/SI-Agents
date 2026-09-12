import pytest

from core.marketplace.registry import (
    EcosystemManager,
    GovernanceDecision,
    Lifecycle,
    MarketplaceManifest,
    MarketplaceRegistry,
    Provenance,
    TrustLevel,
    Version,
)


def manifest(package="demo", version="1.0.0", *, deps=(), permissions=("read",), trust=TrustLevel.CURATED, compatibility=("si.v4",), digest=None, description=""):
    return MarketplaceManifest(
        package,
        Version.parse(version),
        "agent",
        tuple((name, Version.parse(v)) for name, v in deps),
        compatibility,
        permissions,
        Provenance("publisher", "registry", "sha256:" + "1" * 64, trust),
        digest or "sha256:" + "2" * 64,
        description,
    )


def test_strict_versions_and_manifest_identity_are_deterministic():
    assert str(Version.parse("1.2.3")) == "1.2.3"
    with pytest.raises(ValueError):
        Version.parse("1.2")
    assert manifest().manifest_digest == manifest().manifest_digest


def test_registry_rejects_duplicate_versions_and_sorts_versions():
    registry = MarketplaceRegistry()
    registry.publish(manifest(version="1.0.0"))
    registry.publish(manifest(version="2.0.0"))
    with pytest.raises(ValueError):
        registry.publish(manifest(version="2.0.0"))
    assert registry.versions("demo") == (Version(1, 0, 0), Version(2, 0, 0))
    assert registry.get("demo").version == Version(2, 0, 0)


def test_install_requires_compatibility_trust_and_declared_permissions():
    registry = MarketplaceRegistry()
    registry.publish(manifest(trust=TrustLevel.UNTRUSTED))
    manager = EcosystemManager(registry)
    with pytest.raises(PermissionError):
        manager.install("demo")

    registry = MarketplaceRegistry()
    registry.publish(manifest(compatibility=("si.v3",)))
    manager = EcosystemManager(registry)
    with pytest.raises(ValueError, match="incompatible"):
        manager.install("demo")

    registry = MarketplaceRegistry()
    registry.publish(manifest(permissions=("read",)))
    manager = EcosystemManager(registry)
    with pytest.raises(PermissionError, match="not declared"):
        manager.install("demo", requested_permissions=("write",))


def test_governance_binds_to_exact_manifest_digest():
    registry = MarketplaceRegistry()
    item = manifest()
    registry.publish(item)
    calls = []

    def gate(value):
        calls.append(value.manifest_digest)
        return GovernanceDecision(True, "approved", value.manifest_digest)

    manager = EcosystemManager(registry, governance=gate)
    record = manager.install("demo")
    assert record.manifest_digest == item.manifest_digest
    assert calls == [item.manifest_digest]

    bad = EcosystemManager(registry, governance=lambda value: GovernanceDecision(True, "bad", "sha256:" + "0" * 64))
    with pytest.raises(PermissionError):
        bad.install("demo")


def test_dependencies_must_be_installed_at_or_above_required_version():
    registry = MarketplaceRegistry()
    registry.publish(manifest("base", "1.0.0"))
    registry.publish(manifest("base", "2.0.0"))
    registry.publish(manifest("child", "1.0.0", deps=(("base", "2.0.0"),)))
    manager = EcosystemManager(registry)
    with pytest.raises(ValueError, match="unsatisfied dependency"):
        manager.install("child")
    manager.install("base", Version(2, 0, 0))
    assert manager.install("child").version == Version(1, 0, 0)


def test_update_uninstall_and_rollback_preserve_bounded_history():
    registry = MarketplaceRegistry()
    for version in ("1.0.0", "2.0.0", "3.0.0"):
        registry.publish(manifest(version=version))
    manager = EcosystemManager(registry)
    manager.install("demo", Version(1, 0, 0))
    manager.update("demo", Version(2, 0, 0))
    manager.update("demo", Version(3, 0, 0))
    rolled = manager.rollback("demo")
    assert rolled.version == Version(2, 0, 0)
    assert len(rolled.history) <= 32
    removed = manager.uninstall("demo")
    assert removed.lifecycle is Lifecycle.REMOVED
    with pytest.raises(ValueError):
        manager.rollback("demo")


def test_update_cannot_downgrade_or_reinstall():
    registry = MarketplaceRegistry()
    registry.publish(manifest(version="1.0.0"))
    registry.publish(manifest(version="2.0.0"))
    manager = EcosystemManager(registry)
    manager.install("demo", Version(1, 0, 0))
    with pytest.raises(ValueError, match="increase"):
        manager.update("demo", Version(1, 0, 0))
    with pytest.raises(ValueError, match="already installed"):
        manager.install("demo", Version(2, 0, 0))


def test_drift_is_false_for_recorded_manifest_and_detects_metadata_replacement():
    registry = MarketplaceRegistry()
    registry.publish(manifest())
    manager = EcosystemManager(registry)
    manager.install("demo")
    assert manager.detect_drift("demo") is False
    registry._packages["demo"][Version(1, 0, 0)] = manifest(description="changed")
    assert manager.detect_drift("demo") is True


def test_templates_are_unique_and_retrievable():
    registry = MarketplaceRegistry()
    item = manifest()
    registry.register_template("starter", item)
    assert registry.template("starter") == item
    with pytest.raises(ValueError):
        registry.register_template("starter", item)
    with pytest.raises(ValueError):
        registry.register_template("../unsafe", item)


def test_manifest_rejects_duplicate_permissions_dependencies_and_invalid_digest():
    with pytest.raises(ValueError):
        manifest(permissions=("read", "read"))
    with pytest.raises(ValueError):
        manifest(deps=(("base", "1.0.0"), ("base", "1.0.0")))
    with pytest.raises(ValueError):
        manifest(digest="not-a-digest")
