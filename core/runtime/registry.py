"""Explicit harness registration; registration grants no execution permission."""

from core.runtime.protocol import HarnessAdapter


class HarnessRegistry:
    """Deny-by-default registry for transport adapters."""

    def __init__(self) -> None:
        self._adapters: dict[str, HarnessAdapter] = {}
        self._enabled: set[str] = set()

    def register(self, adapter: HarnessAdapter, *, enabled: bool = False) -> None:
        harness_id = adapter.metadata.harness_id
        if harness_id in self._adapters:
            raise ValueError("duplicate harness_id")
        if not isinstance(harness_id, str) or not harness_id.strip():
            raise ValueError("harness_id must not be empty")
        self._adapters[harness_id] = adapter
        if enabled:
            self._enabled.add(harness_id)

    def enable(self, harness_id: str) -> None:
        if harness_id not in self._adapters:
            raise KeyError(harness_id)
        self._enabled.add(harness_id)

    def disable(self, harness_id: str) -> None:
        self._enabled.discard(harness_id)

    def get(self, harness_id: str) -> HarnessAdapter:
        if harness_id not in self._adapters:
            raise KeyError(harness_id)
        if harness_id not in self._enabled:
            raise PermissionError("harness is not enabled")
        return self._adapters[harness_id]

    def is_enabled(self, harness_id: str) -> bool:
        return harness_id in self._enabled

    def all(self) -> tuple[HarnessAdapter, ...]:
        return tuple(self._adapters[key] for key in sorted(self._adapters))

    def enabled(self) -> tuple[HarnessAdapter, ...]:
        return tuple(self._adapters[key] for key in sorted(self._enabled))
