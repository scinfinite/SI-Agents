"""Harness adapter protocol and normalization helpers."""

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from core.runtime.models import InvocationRequest, InvocationResponse, RuntimeCapabilities, RuntimeKind


@dataclass(frozen=True)
class HarnessMetadata:
    harness_id: str
    kind: RuntimeKind
    version: str

    def __post_init__(self) -> None:
        if not self.harness_id.strip() or not self.version.strip():
            raise ValueError("harness metadata requires id and version")


@runtime_checkable
class HarnessAdapter(Protocol):
    @property
    def metadata(self) -> HarnessMetadata: ...

    @property
    def capabilities(self) -> RuntimeCapabilities: ...

    def invoke(self, request: InvocationRequest) -> InvocationResponse: ...

    def cancel(self, request_id: str) -> bool: ...


def normalize_metadata(metadata: dict[str, object]) -> tuple[tuple[str, str], ...]:
    """Normalize transport-specific metadata into a deterministic envelope."""
    return tuple(sorted((str(key), str(value)) for key, value in metadata.items()))
