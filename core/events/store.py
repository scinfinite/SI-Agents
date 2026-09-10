from __future__ import annotations

from threading import RLock

from core.events.models import Event


class EventStore:
    """Bounded append-only event journal for the current process."""

    def __init__(self, *, max_events: int = 10_000) -> None:
        if max_events < 1:
            raise ValueError("max_events must be positive")
        self._max_events = max_events
        self._events: list[Event] = []
        self._lock = RLock()

    def append(self, event: Event) -> None:
        with self._lock:
            self._events.append(event)
            if len(self._events) > self._max_events:
                del self._events[: len(self._events) - self._max_events]

    def all(self) -> tuple[Event, ...]:
        with self._lock:
            return tuple(self._events)

    def by_name(self, name: str) -> tuple[Event, ...]:
        return tuple(event for event in self.all() if event.name == name)

    def by_correlation(self, correlation_id: str) -> tuple[Event, ...]:
        return tuple(event for event in self.all() if event.correlation_id == correlation_id)
