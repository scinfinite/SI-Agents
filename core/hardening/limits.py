"""Explicit resource bounds used by production-facing callers."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceLimits:
    max_input_bytes: int = 1_048_576
    max_output_bytes: int = 4_194_304
    max_events: int = 10_000
    max_metadata_items: int = 64
    max_timeout_seconds: float = 900.0

    def __post_init__(self) -> None:
        if self.max_input_bytes <= 0 or self.max_output_bytes <= 0:
            raise ValueError("byte limits must be positive")
        if self.max_events <= 0 or self.max_metadata_items <= 0:
            raise ValueError("item limits must be positive")
        if self.max_timeout_seconds <= 0:
            raise ValueError("max_timeout_seconds must be positive")

    def validate(self, *, input_bytes: int, output_bytes: int, events: int, metadata_items: int,
                 timeout_seconds: float | None) -> None:
        values = (input_bytes, output_bytes, events, metadata_items)
        if any(value < 0 for value in values):
            raise ValueError("resource measurements must be non-negative")
        if input_bytes > self.max_input_bytes:
            raise ValueError("input exceeds configured limit")
        if output_bytes > self.max_output_bytes:
            raise ValueError("output exceeds configured limit")
        if events > self.max_events:
            raise ValueError("event count exceeds configured limit")
        if metadata_items > self.max_metadata_items:
            raise ValueError("metadata item count exceeds configured limit")
        if timeout_seconds is not None and timeout_seconds > self.max_timeout_seconds:
            raise ValueError("timeout exceeds configured limit")
