"""Harness-neutral adapter contracts for portable V4 resources."""

from dataclasses import dataclass
from enum import Enum
from typing import Protocol, runtime_checkable


class PortableAdapterKind(str, Enum):
    RUNTIME = "runtime"
    SESSION = "session"
    TOOL = "tool"
    MODEL = "model"
    EVENT = "event"
    CAPABILITY = "capability"
    CONTEXT = "context"
    CHECKPOINT = "checkpoint"
    ARTIFACT = "artifact"


@dataclass(frozen=True)
class PortableAdapterDescriptor:
    adapter_id: str
    kind: PortableAdapterKind
    version: str
    capabilities: tuple[str, ...] = ()
    project_scoped: bool = True

    def __post_init__(self) -> None:
        if not self.adapter_id.strip() or not self.version.strip():
            raise ValueError("portable adapter requires id and version")
        if any(not capability.strip() for capability in self.capabilities):
            raise ValueError("portable adapter capabilities cannot be empty")
        if len(set(self.capabilities)) != len(self.capabilities):
            raise ValueError("portable adapter capabilities must be unique")


@runtime_checkable
class PortableAdapter(Protocol):
    """Common discovery contract; data and authority remain owned by SI Core."""

    @property
    def descriptor(self) -> PortableAdapterDescriptor: ...

    def health(self) -> bool: ...


class PortableAdapterRegistry:
    """Deny-by-default registry for resource adapters across runtimes."""

    def __init__(self) -> None:
        self._adapters: dict[str, PortableAdapter] = {}
        self._enabled: set[str] = set()

    def register(self, adapter: PortableAdapter, *, enabled: bool = False) -> None:
        descriptor = adapter.descriptor
        if descriptor.adapter_id in self._adapters:
            raise ValueError("duplicate adapter_id")
        self._adapters[descriptor.adapter_id] = adapter
        if enabled:
            self._enabled.add(descriptor.adapter_id)

    def enable(self, adapter_id: str) -> None:
        if adapter_id not in self._adapters:
            raise KeyError(adapter_id)
        self._enabled.add(adapter_id)

    def disable(self, adapter_id: str) -> None:
        self._enabled.discard(adapter_id)

    def enabled(self, *, kind: PortableAdapterKind | None = None) -> tuple[PortableAdapter, ...]:
        adapters = [self._adapters[key] for key in sorted(self._enabled)]
        if kind is not None:
            adapters = [adapter for adapter in adapters if adapter.descriptor.kind is kind]
        return tuple(adapters)

    def discover(self) -> tuple[PortableAdapterDescriptor, ...]:
        return tuple(self._adapters[key].descriptor for key in sorted(self._adapters))
