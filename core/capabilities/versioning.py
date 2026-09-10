import re

from core.capabilities.models import Capability
from core.capabilities.registry import CapabilityRegistry

_VERSION = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def validate_version(version: str) -> str:
    if not _VERSION.fullmatch(version):
        raise ValueError("Capability version must use MAJOR.MINOR.PATCH")
    return version


def bump_version(version: str, *, part: str) -> str:
    validate_version(version)
    major, minor, patch = (int(value) for value in version.split("."))
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    if part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise ValueError("Version part must be major, minor, or patch")


class CapabilityVersionManager:
    def __init__(self, registry: CapabilityRegistry) -> None:
        self.registry = registry

    def set_version(self, capability_id: str, version: str) -> Capability:
        current = self.registry.get(capability_id)
        updated = Capability(**{**current.__dict__, "version": validate_version(version)})
        return self.registry.replace(updated)

    def bump(self, capability_id: str, *, part: str) -> Capability:
        current = self.registry.get(capability_id)
        version = current.version or "0.1.0"
        return self.set_version(capability_id, bump_version(version, part=part))
