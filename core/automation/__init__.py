"""Automation primitives and the Phase 65 workflow state machine."""

from core.automation.models import (
    AutomationJob,
    JobState,
    RetryPolicy,
    RunRecord,
    RunStatus,
    Schedule,
    ScheduleKind,
)
from core.automation.registry import AutomationRegistry
from core.automation.runner import AutomationRunner
from core.automation.scheduler import AutomationScheduler
from core.automation.store import AutomationStore
from core.automation.workflow_io import export_definition, import_definition
from core.automation.workflows import (
    TriggerKind,
    WorkflowDefinition,
    WorkflowEngine,
    WorkflowRun,
    WorkflowRunStatus,
    WorkflowStep,
    WorkflowStepKind,
    WorkflowTrigger,
)

__all__ = [
    "AutomationJob",
    "AutomationRegistry",
    "AutomationRunner",
    "AutomationScheduler",
    "AutomationStore",
    "JobState",
    "RetryPolicy",
    "RunRecord",
    "RunStatus",
    "Schedule",
    "ScheduleKind",
    "TriggerKind",
    "WorkflowDefinition",
    "WorkflowEngine",
    "WorkflowRun",
    "WorkflowRunStatus",
    "WorkflowStep",
    "WorkflowStepKind",
    "WorkflowTrigger",
    "export_definition",
    "import_definition",
]
