from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from core.capabilities.registry import CapabilityRegistry
from core.execution.command_runner import CommandRunner
from core.execution.execution_record import ExecutionRecord
from core.orchestrator.agent_coordinator import AgentCoordinator
from core.orchestrator.brain import BrainResult, EngineeringBrain
from core.orchestrator.brain_models import Problem
from core.orchestrator.capability_selector import CapabilitySelector
from core.orchestrator.context_manager import ContextManager
from core.orchestrator.task_manager import TaskManager
from core.policies.approval_engine import ApprovalEngine
from core.policies.permission_engine import PermissionEngine
from core.skills.executor import SkillExecutor
from core.skills.models import Skill, SkillResult
from core.skills.registry import SkillRegistry
from core.state.checkpoints import Checkpoint, CheckpointStore
from core.state.execution_state import ExecutionState
from core.state.execution_state_store import ExecutionStateStore
from core.state.filesystem_snapshot import FilesystemSnapshotStore
from core.verification.claim_store import ClaimStore
from core.verification.claims import Claim
from core.verification.evidence import Evidence, VerificationStatus
from core.verification.evidence_store import EvidenceStore
from core.verification.production_readiness import ProductionReadiness, ReadinessGate, evaluate
from core.verification.red_team import RedTeamSuite
from core.verification.regression import RegressionSuite
from core.verification.verification_engine import (
    VerificationCheck,
    VerificationEngine,
    VerificationReport,
)
from tools.registry.builtins import register_builtin_tools
from tools.registry.executor import ToolExecutor
from tools.registry.registry import ToolDescriptor, ToolRegistry


class Orchestrator:
    """Control-plane entry point coordinating tasks, capabilities, tools, skills, and evidence."""

    def __init__(
        self,
        task_manager: TaskManager | None = None,
        checkpoint_store: CheckpointStore | None = None,
        evidence_store: EvidenceStore | None = None,
        command_runner: CommandRunner | None = None,
        snapshot_store: FilesystemSnapshotStore | None = None,
        permission_engine: PermissionEngine | None = None,
        approval_engine: ApprovalEngine | None = None,
        capability_registry: CapabilityRegistry | None = None,
        context_manager: ContextManager | None = None,
        agent_coordinator: AgentCoordinator | None = None,
        execution_state_store: ExecutionStateStore | None = None,
        tool_registry: ToolRegistry | None = None,
        tool_executor: ToolExecutor | None = None,
        skill_registry: SkillRegistry | None = None,
        skill_executor: SkillExecutor | None = None,
        claim_store: ClaimStore | None = None,
    ) -> None:
        self.tasks = task_manager or TaskManager()
        self.checkpoints = checkpoint_store or CheckpointStore()
        self.evidence = evidence_store or EvidenceStore()
        self.claims = claim_store or ClaimStore()
        self.verification = VerificationEngine(self.claims, self.evidence)
        self.commands = command_runner
        self.snapshots = snapshot_store
        self.permissions = permission_engine or PermissionEngine()
        self.approvals = approval_engine or ApprovalEngine()
        self.capabilities = capability_registry or CapabilityRegistry()
        self.capability_selector = CapabilitySelector(self.capabilities)
        self.brain = EngineeringBrain(self.capabilities)
        self.contexts = context_manager or ContextManager()
        self.agents = agent_coordinator or AgentCoordinator()
        self.execution_states = execution_state_store or ExecutionStateStore()
        self.tools = tool_registry or ToolRegistry()
        self.tool_executor = tool_executor or ToolExecutor(self.tools, permissions=self.permissions)
        self.skills = skill_registry or SkillRegistry()
        self.skill_executor = skill_executor or SkillExecutor(
            self.skills, self.permissions, self.evidence
        )

    def run(self, description: str, worker: Callable[[str], str]) -> str:
        task = self.tasks.create(description)
        task.start()
        self.tasks.persist()
        self.contexts.get_or_create(task.id)
        try:
            result = worker(task.description)
        except Exception as exc:
            task.fail(str(exc))
            self.tasks.persist()
            raise
        task.succeed(result)
        self.tasks.persist()
        return result

    def build_plan(self, problem: Problem, *, capability_category: str | None = None) -> BrainResult:
        """Build and validate an engineering plan without executing it."""
        return self.brain.build(problem, category=capability_category)

    def register_builtin_tools(self) -> None:
        """Register standard tool descriptors; registration grants no permissions."""
        register_builtin_tools(self.tools)

    def register_tool(self, tool: ToolDescriptor) -> ToolDescriptor:
        """Register a tool descriptor without executing or authorizing it."""
        return self.tools.register(tool)

    def bind_tool(self, tool_id: str, implementation: object) -> None:
        self.tool_executor.bind(tool_id, implementation)

    def invoke_tool(
        self,
        tool_id: str,
        operation: str,
        *args: Any,
        agent: str | None = None,
        approval_granted: bool = False,
        **kwargs: Any,
    ) -> Any:
        return self.tool_executor.invoke(
            tool_id, operation, *args, agent=agent, approval_granted=approval_granted, **kwargs
        )

    def register_skill(self, skill: Skill) -> Skill:
        """Register a reusable skill; registration never grants execution permission."""
        return self.skills.register(skill)

    def select_skills(
        self,
        *,
        category: str | None = None,
        required_tools: tuple[str, ...] = (),
        required_permissions: tuple[str, ...] = (),
        validated_only: bool = True,
    ) -> tuple[Skill, ...]:
        return self.skills.select(
            category=category,
            required_tools=required_tools,
            required_permissions=required_permissions,
            validated_only=validated_only,
        )

    def execute_skill(
        self,
        skill_id: str,
        handler: Callable[[Mapping[str, object]], Mapping[str, object]],
        inputs: Mapping[str, object],
        *,
        agent: str | None = None,
        approval_granted: bool = False,
        verifier: Callable[[Mapping[str, object]], bool] | None = None,
    ) -> SkillResult:
        return self.skill_executor.execute(
            skill_id,
            handler,
            inputs,
            agent=agent,
            approval_granted=approval_granted,
            verifier=verifier,
        )

    def register_claim(self, claim: Claim) -> Claim:
        """Register a bounded engineering claim before attempting to verify it."""
        return self.claims.record(claim)

    def verify_claim(
        self,
        claim_id: str,
        checks: tuple[VerificationCheck, ...],
        *,
        regression: RegressionSuite | None = None,
        red_team: RedTeamSuite | None = None,
        source_prefix: str = "verification",
    ) -> VerificationReport:
        claim = self.claims.get(claim_id)
        return self.verification.verify(
            claim,
            checks,
            regression=regression,
            red_team=red_team,
            source_prefix=source_prefix,
        )

    def evaluate_readiness(self, gates: tuple[ReadinessGate, ...]) -> ProductionReadiness:
        """Evaluate release readiness; no gate is considered passed without evidence."""
        return evaluate(gates)

    def select_capabilities(
        self,
        *,
        category: str,
        required_tools: tuple[str, ...] = (),
        required_permissions: tuple[str, ...] = (),
        validated_only: bool = True,
    ):
        """Select capabilities; selection never grants execution permission."""
        return self.capability_selector.select(
            category=category,
            required_tools=required_tools,
            required_permissions=required_permissions,
            validated_only=validated_only,
        )

    def checkpoint(
        self,
        task_id: str,
        description: str,
        *,
        workspace: str | Path | None = None,
    ) -> Checkpoint:
        """Record a checkpoint, optionally backed by a filesystem snapshot."""
        self.tasks.get(task_id)
        snapshot_id = None
        if workspace is not None:
            if self.snapshots is None:
                raise RuntimeError("Snapshot store is not configured")
            snapshot_id = self.snapshots.create(workspace).id
        return self.checkpoints.create(task_id, description, snapshot_id=snapshot_id)

    def restore_checkpoint(self, checkpoint_id: str, *, approval_granted: bool = False) -> None:
        """Restore a snapshot-backed checkpoint with explicit destructive approval."""
        checkpoint = self.checkpoints.get(checkpoint_id)
        if checkpoint.snapshot_id is None:
            raise RuntimeError("Checkpoint has no workspace snapshot")
        if self.snapshots is None:
            raise RuntimeError("Snapshot store is not configured")
        self.snapshots.restore(checkpoint.snapshot_id, approval_granted=approval_granted)

    def execute(
        self,
        task_id: str,
        command: str,
        *,
        timeout: float = 60.0,
        agent: str | None = None,
        tool: str | None = None,
        approval_granted: bool = False,
    ) -> ExecutionRecord:
        """Execute a command for a known task and record state and evidence."""
        if self.commands is None:
            raise RuntimeError("Command runner is not configured")
        task = self.tasks.get(task_id)
        if task.status.value != "running":
            raise ValueError(f"Cannot execute command for task in state {task.status.value}")
        self.permissions.require(
            "local_command", approval_granted=approval_granted, agent=agent, tool=tool
        )
        state = ExecutionState(task_id=task_id)
        self.execution_states.record(state)
        state.start()
        self.execution_states.update(state)
        try:
            record = self.commands.run(task_id, command, timeout=timeout)
        except Exception as exc:
            state.fail(str(exc))
            self.execution_states.update(state)
            raise
        status = VerificationStatus.VERIFIED if record.succeeded else VerificationStatus.FAILED
        details = record.stderr if not record.succeeded else record.stdout
        if record.succeeded:
            state.succeed()
        else:
            state.fail(details or f"Command returned {record.return_code}")
        self.execution_states.update(state)
        self.evidence.record(
            Evidence(
                claim=f"Command execution succeeded: {record.succeeded}",
                source=f"execution:{record.id}",
                verification_status=status,
                details=details,
            )
        )
        return record
