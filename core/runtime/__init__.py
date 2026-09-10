"""Harness and runtime interoperability primitives."""

from core.runtime.conformance import ConformanceFailure, run_conformance
from core.runtime.local import LocalHarnessAdapter
from core.runtime.models import (
    InvocationRequest,
    InvocationResponse,
    InvocationStatus,
    RuntimeCapabilities,
    RuntimeError,
    RuntimeErrorCode,
    RuntimeEvent,
    RuntimeEventType,
    RuntimeKind,
)
from core.runtime.protocol import HarnessAdapter, HarnessMetadata, normalize_metadata
from core.runtime.registry import HarnessRegistry
from core.runtime.session import RuntimeSession, SessionRegistry, SessionStatus

__all__ = [
    "ConformanceFailure", "HarnessAdapter", "HarnessMetadata", "HarnessRegistry",
    "InvocationRequest", "InvocationResponse", "InvocationStatus", "LocalHarnessAdapter",
    "RuntimeCapabilities", "RuntimeError", "RuntimeErrorCode", "RuntimeEvent", "RuntimeEventType",
    "RuntimeKind", "RuntimeSession", "SessionRegistry", "SessionStatus",
    "normalize_metadata", "run_conformance",
]
