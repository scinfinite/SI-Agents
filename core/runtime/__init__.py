"""Harness interoperability, durable execution, scheduling, and V4 runtime primitives."""

from core.runtime.bridge import CallbackHarnessAdapter, adapter_metadata, is_harness_adapter
from core.runtime.checkpoints import Checkpoint, CheckpointError, CheckpointStore, ResumePlan
from core.runtime.conformance import ConformanceFailure, run_conformance
from core.runtime.cross_runtime import CrossRuntimeGateway, HarnessDescriptor, HarnessHealth, RouteDecision
from core.runtime.deployment import HarnessDeploymentManifest, build_manifest
from core.runtime.engine import RuntimeEngine
from core.runtime.events import EventBus, RuntimeEventRecord
from core.runtime.execution import AuthorizedTask, Attempt, Execution, ExecutionRuntime, ExecutionStore, RuntimeAdapter, RuntimeFailure, State
from core.runtime.local import LocalHarnessAdapter
from core.runtime.models import InvocationRequest, InvocationResponse, InvocationStatus, RuntimeCapabilities, RuntimeError, RuntimeErrorCode, RuntimeEvent, RuntimeEventType, RuntimeKind
from core.runtime.omniroute import OmniRouteBridge, OmniRouteCredentialRef, OmniRouteModel, OmniRoutePolicy, OmniRouteTransportError
from core.runtime.opencode import OpenCodeBridge, OpenCodeSession, OpenCodeTransportError
from core.runtime.protocol import HarnessAdapter, HarnessMetadata, normalize_metadata
from core.runtime.registry import HarnessRegistry
from core.runtime.scheduler import ParallelScheduler, ScheduledItem, ScheduleState
from core.runtime.session import RuntimeSession, SessionRegistry, SessionStatus
from core.runtime.wire import WIRE_PROTOCOL, capabilities_to_dict, request_to_dict, response_to_dict

__all__ = [
    "WIRE_PROTOCOL", "AuthorizedTask", "Attempt", "CallbackHarnessAdapter", "Checkpoint", "CheckpointError",
    "CheckpointStore", "ConformanceFailure", "CrossRuntimeGateway", "EventBus", "Execution", "ExecutionRuntime", "ExecutionStore",
    "HarnessAdapter", "HarnessDeploymentManifest", "HarnessDescriptor", "HarnessHealth", "HarnessMetadata", "HarnessRegistry", "InvocationRequest",
    "InvocationResponse", "InvocationStatus", "LocalHarnessAdapter", "OmniRouteBridge", "OmniRouteCredentialRef", "OmniRouteModel", "OmniRoutePolicy",
    "OmniRouteTransportError", "OpenCodeBridge", "OpenCodeSession", "OpenCodeTransportError", "ParallelScheduler", "ResumePlan", "RouteDecision",
    "RuntimeAdapter", "RuntimeCapabilities", "RuntimeEngine", "RuntimeError", "RuntimeErrorCode", "RuntimeEvent", "RuntimeEventRecord", "RuntimeEventType",
    "RuntimeFailure", "RuntimeKind", "RuntimeSession", "ScheduleState", "ScheduledItem", "SessionRegistry", "SessionStatus", "State", "adapter_metadata",
    "build_manifest", "capabilities_to_dict", "is_harness_adapter", "normalize_metadata", "request_to_dict", "response_to_dict", "run_conformance",
]
