from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from agents.base import AgentContext, AgentResult
from agents.debugger import DebuggerAgent
from agents.developer import DeveloperAgent
from agents.tester import TesterAgent
from core.orchestrator.brain_models import Problem
from core.orchestrator.orchestrator import Orchestrator
from core.orchestrator.plan_models import Plan, StepKind
from core.verification.evidence import Evidence, VerificationStatus


@dataclass(frozen=True)
class EngineeringWorkflowResult:
    task_id: str
    checkpoint_id: str
    debugger: AgentResult
    developer: AgentResult
    tester: AgentResult
    plan_id: str | None = None


class EngineeringWorkflow:
    """Execute the first engineering loop through explicit agent handoffs and gates."""

    def __init__(self, orchestrator: Orchestrator) -> None:
        self.orchestrator = orchestrator
        self.debugger = DebuggerAgent()
        self.developer = DeveloperAgent()
        self.tester = TesterAgent()

    def run(
        self,
        description: str,
        *,
        inspect: Callable[[], str],
        reproduce: Callable[[], bool],
        diagnose: Callable[[], str],
        repair: Callable[[str], str],
        verify: Callable[[], bool],
        red_team: Callable[[], bool],
        regression: Callable[[], bool],
        problem: Problem | None = None,
        workspace: str | None = None,
    ) -> EngineeringWorkflowResult:
        task = self.orchestrator.tasks.create(description)
        task.start()
        context = AgentContext(task.id)
        plan_id = None
        try:
            if problem is not None:
                brain_result = self.orchestrator.build_plan(problem)
                self._validate_agent_plan(brain_result.plan)
                plan_id = brain_result.plan.id
                context.values["brain_plan"] = brain_result.plan
                self._evidence(task.id, "Engineering Brain plan validated", plan_id)

            self.orchestrator.permissions.require("repository_read", agent="debugger")
            inspection = inspect().strip()
            if not inspection:
                raise RuntimeError("Inspection produced no result")
            context.values["inspection"] = inspection
            self._evidence(task.id, "Inspection completed", inspection)

            checkpoint = self.orchestrator.checkpoint(task.id, "Before repair", workspace=workspace)
            self._evidence(task.id, "Repair checkpoint created", checkpoint.id)

            debugger = self.debugger.run(
                context, reproduce, diagnose, permissions=self.orchestrator.permissions
            )
            self._evidence(task.id, debugger.summary, str(debugger.handoff))
            developer = self.developer.run(
                context, repair, permissions=self.orchestrator.permissions
            )
            self._evidence(task.id, developer.summary, str(developer.handoff))
            tester = self.tester.run(
                context, verify, red_team, regression, permissions=self.orchestrator.permissions
            )
            self._evidence(task.id, tester.summary, str(tester.handoff))
        except Exception as exc:
            task.fail(str(exc))
            self._evidence(task.id, "Engineering workflow failed", str(exc), failed=True)
            self.orchestrator.tasks.persist()
            raise
        task.succeed("Engineering workflow verified")
        self.orchestrator.tasks.persist()
        return EngineeringWorkflowResult(task.id, checkpoint.id, debugger, developer, tester, plan_id)

    @staticmethod
    def _validate_agent_plan(plan: Plan) -> None:
        kinds = {step.kind for step in plan.steps}
        required = (StepKind.INSPECT, StepKind.RESEARCH, StepKind.EXECUTE, StepKind.TEST, StepKind.VERIFY, StepKind.DOCUMENT)
        if any(kind not in kinds for kind in required):
            raise RuntimeError("Engineering Brain plan is missing a required workflow stage")

    def _evidence(self, task_id: str, claim: str, details: str, *, failed: bool = False) -> None:
        self.orchestrator.evidence.record(
            Evidence(
                claim=claim,
                source=f"engineering-workflow:{task_id}",
                verification_status=VerificationStatus.FAILED if failed else VerificationStatus.VERIFIED,
                details=details,
            )
        )
