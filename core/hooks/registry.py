from __future__ import annotations

from threading import RLock

from core.hooks.models import Hook


class HookRegistry:
    """Explicit hook registration with stable ordering and duplicate rejection."""

    def __init__(self, *, max_hooks_per_event: int = 32) -> None:
        if max_hooks_per_event < 1:
            raise ValueError("max_hooks_per_event must be positive")
        self._max_hooks_per_event = max_hooks_per_event
        self._hooks: dict[str, Hook] = {}
        self._lock = RLock()

    def register(self, hook: Hook) -> None:
        with self._lock:
            if hook.id in self._hooks:
                raise ValueError(f"duplicate hook: {hook.id}")
            for event in hook.events:
                count = sum(event in existing.events for existing in self._hooks.values())
                if count >= self._max_hooks_per_event:
                    raise ValueError(f"hook limit reached for event: {event}")
            self._hooks[hook.id] = hook

    def get(self, hook_id: str) -> Hook:
        with self._lock:
            try:
                return self._hooks[hook_id]
            except KeyError as exc:
                raise KeyError(f"unknown hook: {hook_id}") from exc

    def matching(self, event_name: str, phase: str) -> tuple[Hook, ...]:
        with self._lock:
            return tuple(
                sorted(
                    (
                        hook
                        for hook in self._hooks.values()
                        if event_name in hook.events and hook.phase.value == phase
                    ),
                    key=lambda item: (item.priority, item.id),
                )
            )

    def all(self) -> tuple[Hook, ...]:
        with self._lock:
            return tuple(sorted(self._hooks.values(), key=lambda item: (item.priority, item.id)))
