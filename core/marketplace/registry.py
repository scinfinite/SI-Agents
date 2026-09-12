"""Deny-by-default marketplace registry and lifecycle manager.

The marketplace stores metadata and lifecycle state only. Installation never
implicitly grants execution authority; governance and SI Core authorization
remain authoritative.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from hashlib import sha256
import re
from typing import Callable

_MAX_ID = 128
_MAX_ITEMS = 128
_MAX_HISTORY = 32


class TrustLevel(str, Enum):
    UNTRUSTED = "untrusted"
    VERIFIED = "verified"
    CURATED = "curated"


class Lifecycle(str, Enum):
    INSTALLED = "installed"
    REMOVED = "removed"


@dataclass(frozen=True, order=True)
class Version:
    major: int
    minor: int = 0
    patch: int = 0

    @classmethod
    def parse(cls, value: str) -> "Version":
        if not isinstance(value, str) or not re.fullmatch(r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)", value):
            raise ValueError("version must be strict semver MAJOR.MINOR.PATCH")
        return cls(*(int(part) for part in value.split(".")))

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


@dataclass(frozen=True)
class Provenance:
    publisher: str
    source: str
    artifact_digest: str
    trust: TrustLevel

    def __post_init__(self) -> None:
        for value in (self.publisher, self.source, self.artifact_digest):
            if not isinstance(value, str) or not value.strip() or len(value) > _MAX_ID * 4:
                raise ValueError("provenance fields are required and bounded")
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", self.artifact_digest):
            raise ValueError("artifact_digest must be a sha256 digest")


@dataclass(frozen=True)
class MarketplaceManifest:
    package_id: str
    version: Version
    kind: str
    dependencies: tuple[tuple[str, Version], ...] = ()
    compatibility: tuple[str, ...] = ()
    permissions: tuple[str, ...] = ()
    provenance: Provenance = field(default_factory=lambda: Provenance("unknown", "unknown", "sha256:" + "0" * 64, TrustLevel.UNTRUSTED))
    payload_digest: str = "sha256:" + "0" * 64
    description: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.package_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,127}", self.package_id):
            raise ValueError("package_id is invalid or unbounded")
        if not self.kind.strip() or len(self.kind) > _MAX_ID:
            raise ValueError("kind is invalid")
        for name, values in (("compatibility", self.compatibility), ("permissions", self.permissions)):
            if len(values) > _MAX_ITEMS or any(not isinstance(v, str) or not v.strip() or len(v) > _MAX_ID for v in values):
                raise ValueError(f"{name} contains invalid values")
            if len(set(values)) != len(values):
                raise ValueError(f"{name} must be unique")
        if len(self.dependencies) > _MAX_ITEMS or len({name for name, _ in self.dependencies}) != len(self.dependencies):
            raise ValueError("dependencies must be unique and bounded")
        if any(not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,127}", name) for name, _ in self.dependencies):
            raise ValueError("dependency id is invalid")
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", self.payload_digest):
            raise ValueError("payload_digest must be a sha256 digest")

    def canonical(self) -> str:
        deps = ",".join(f"{name}@{version}" for name, version in sorted(self.dependencies))
        return "|".join((self.package_id, str(self.version), self.kind, deps, ",".join(sorted(self.compatibility)), ",".join(sorted(self.permissions)), self.provenance.publisher, self.provenance.source, self.provenance.artifact_digest, self.provenance.trust.value, self.payload_digest))

    @property
    def manifest_digest(self) -> str:
        return "sha256:" + sha256(self.canonical().encode()).hexdigest()


@dataclass(frozen=True)
class GovernanceDecision:
    allowed: bool
    reason: str
    manifest_digest: str


@dataclass(frozen=True)
class InstallRecord:
    package_id: str
    version: Version
    manifest_digest: str
    lifecycle: Lifecycle
    history: tuple[Version, ...]


GovernanceHook = Callable[[MarketplaceManifest], GovernanceDecision]


class MarketplaceRegistry:
    """Deterministic metadata registry; it does not execute package payloads."""

    def __init__(self) -> None:
        self._packages: dict[str, dict[Version, MarketplaceManifest]] = {}
        self._templates: dict[str, MarketplaceManifest] = {}

    def publish(self, manifest: MarketplaceManifest) -> None:
        versions = self._packages.setdefault(manifest.package_id, {})
        if manifest.version in versions:
            raise ValueError("duplicate package version")
        versions[manifest.version] = manifest

    def get(self, package_id: str, version: Version | None = None) -> MarketplaceManifest:
        versions = self._packages.get(package_id)
        if not versions:
            raise KeyError(package_id)
        if version is None:
            return versions[max(versions)]
        try:
            return versions[version]
        except KeyError:
            raise KeyError(f"{package_id}@{version}") from None

    def versions(self, package_id: str) -> tuple[Version, ...]:
        return tuple(sorted(self._packages.get(package_id, {})))

    def register_template(self, template_id: str, manifest: MarketplaceManifest) -> None:
        if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,127}", template_id):
            raise ValueError("template_id is invalid")
        if template_id in self._templates:
            raise ValueError("duplicate template")
        self._templates[template_id] = manifest

    def template(self, template_id: str) -> MarketplaceManifest:
        return self._templates[template_id]


class EcosystemManager:
    """Governed install/update/remove/rollback and drift detection."""

    def __init__(self, registry: MarketplaceRegistry, *, governance: GovernanceHook | None = None, compatible_with: str = "si.v4") -> None:
        self.registry = registry
        self.governance = governance
        self.compatible_with = compatible_with
        self._installed: dict[str, InstallRecord] = {}

    def _check(self, manifest: MarketplaceManifest, *, requested_permissions: tuple[str, ...] = ()) -> None:
        if self.governance is not None:
            decision = self.governance(manifest)
            if not decision.allowed or decision.manifest_digest != manifest.manifest_digest:
                raise PermissionError("governance gate rejected manifest")
        if self.compatible_with not in manifest.compatibility:
            raise ValueError("package is incompatible with this SI runtime")
        if not set(requested_permissions).issubset(manifest.permissions):
            raise PermissionError("requested permission is not declared by manifest")
        if manifest.provenance.trust is TrustLevel.UNTRUSTED:
            raise PermissionError("untrusted package requires explicit governance")
        for dependency, required in manifest.dependencies:
            installed = self._installed.get(dependency)
            if installed is None or installed.lifecycle is not Lifecycle.INSTALLED or installed.version < required:
                raise ValueError(f"unsatisfied dependency: {dependency}@{required}")

    def install(self, package_id: str, version: Version | None = None, *, requested_permissions: tuple[str, ...] = ()) -> InstallRecord:
        manifest = self.registry.get(package_id, version)
        self._check(manifest, requested_permissions=requested_permissions)
        if package_id in self._installed and self._installed[package_id].lifecycle is Lifecycle.INSTALLED:
            raise ValueError("package already installed; use update")
        record = InstallRecord(package_id, manifest.version, manifest.manifest_digest, Lifecycle.INSTALLED, (manifest.version,))
        self._installed[package_id] = record
        return record

    def update(self, package_id: str, version: Version, *, requested_permissions: tuple[str, ...] = ()) -> InstallRecord:
        current = self._installed.get(package_id)
        if current is None or current.lifecycle is not Lifecycle.INSTALLED:
            raise KeyError(package_id)
        manifest = self.registry.get(package_id, version)
        if manifest.version <= current.version:
            raise ValueError("update must increase version")
        self._check(manifest, requested_permissions=requested_permissions)
        history = (current.history + (manifest.version,))[-_MAX_HISTORY:]
        record = InstallRecord(package_id, manifest.version, manifest.manifest_digest, Lifecycle.INSTALLED, history)
        self._installed[package_id] = record
        return record

    def uninstall(self, package_id: str) -> InstallRecord:
        current = self._installed.get(package_id)
        if current is None or current.lifecycle is not Lifecycle.INSTALLED:
            raise KeyError(package_id)
        record = InstallRecord(package_id, current.version, current.manifest_digest, Lifecycle.REMOVED, current.history)
        self._installed[package_id] = record
        return record

    def rollback(self, package_id: str) -> InstallRecord:
        current = self._installed.get(package_id)
        if current is None or current.lifecycle is not Lifecycle.INSTALLED or len(current.history) < 2:
            raise ValueError("no previous installed version")
        target = current.history[-2]
        manifest = self.registry.get(package_id, target)
        self._check(manifest)
        history = (current.history + (target,))[-_MAX_HISTORY:]
        record = InstallRecord(package_id, target, manifest.manifest_digest, Lifecycle.INSTALLED, history)
        self._installed[package_id] = record
        return record

    def installed(self, package_id: str) -> InstallRecord:
        return self._installed[package_id]

    def detect_drift(self, package_id: str) -> bool:
        current = self._installed.get(package_id)
        if current is None or current.lifecycle is not Lifecycle.INSTALLED:
            raise KeyError(package_id)
        return self.registry.get(package_id, current.version).manifest_digest != current.manifest_digest
