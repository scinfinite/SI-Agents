"""Harness interoperability, durable execution, scheduling, and V4 event primitives."""

from core.runtime.bridge import CallbackHarnessAdapter, adapter_metadata, is_harness_adapter
from core.runtime.conformance import ConformanceFailure, run_conformance
from core.runtime.deployment import HarnessDeploymentManifest, build_manifest
from core.runtime.engine import RuntimeEngine
from core.runtime.events import EventBus, RuntimeEventRecord
from core.runtime.execution import AuthorizedTask, Attempt, Execution, ExecutionRuntime, ExecutionStore, RuntimeAdapter, RuntimeFailure, State
from core.runtime.local import LocalHarnessAdapter
from core.runtime.models import InvocationRequest, InvocationResponse, InvocationStatus, RuntimeCapabilities, RuntimeError, RuntimeErrorCode, RuntimeEvent, RuntimeEventType, RuntimeKind
from core.runtime.opencode import OpenCodeBridge, OpenCodeSession, OpenCodeTransportError
from core.runtime.protocol import HarnessAdapter, HarnessMetadata, normalize_metadata
from core.runtime.registry import HarnessRegistry
from core.runtime.scheduler import ParallelScheduler, ScheduledItem, ScheduleState
from core.runtime.session import RuntimeSession, SessionRegistry, SessionStatus
from core.runtime.wire import WIRE_PROTOCOL, capabilities_to_dict, request_to_dict, response_to_dict

__all__ = [
    "WIRE_PROTOCOL", "AuthorizedTask", "Attempt", "CallbackHarnessAdapter", "ConformanceFailure",
    "EventBus", "Execution", "ExecutionRuntime", "ExecutionStore", "HarnessAdapter", "HarnessDeploymentManifest",
    "HarnessMetadata", "HarnessRegistry", "InvocationRequest", "InvocationResponse", "InvocationStatus",
    "LocalHarnessAdapter", "OpenCodeBridge", "OpenCodeSession", "OpenCodeTransportError", "ParallelScheduler",
    "RuntimeAdapter", "RuntimeCapabilities", "RuntimeEngine", "RuntimeError", "RuntimeErrorCode", "RuntimeEvent",
    "RuntimeEventRecord", "RuntimeEventType", "RuntimeFailure", "RuntimeKind", "RuntimeSession", "ScheduleState",
    "ScheduledItem", "SessionRegistry", "SessionStatus", "State", "adapter_metadata", "build_manifest",
    "capabilities_to_dict", "is_harness_adapter", "normalize_metadata", "request_to_dict", "response_to_dict", "run_conformance",
]
