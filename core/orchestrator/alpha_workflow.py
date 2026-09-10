from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from core.orchestrator.orchestrator import Orchestrator
from core.state.task_state import Task
from core.verification.evidence import Evidence, VerificationStatus


@dataclass(frozen=True)
class AlphaWorkflowResult:
    """Outcome of a deterministic Alpha repair workflow."""

    task: Task
    checkpoint_id: str


class AlphaWorkflow:
    """Enforce the Alpha inspect-repair-verify workflow ordering."""

    def __init__(self, orchestrator: Orchestrator) -> None:
        self.orchestrator = orchestrator

    def run(
        self,
        description: str,
        *,
        inspect: Callable[[], str],
        reproduce: Callable[[], bool],
        repair: Callable[[], str],
        verify: Callable[[], bool],
        red_team: Callable[[], bool],
        regression: Callable[[], bool],
    ) -> AlphaWorkflowResult:
        task = self.orchestrator.tasks.create(description)
        task.start()
        try:
            self._record(task.id, "Architecture inspection completed", inspect())
            if not reproduce():
                raise RuntimeError("Expected failure was not reproduced")
            self._record(task.id, "Broken behavior reproduced", "reproduction returned true")

            checkpoint = self.orchestrator.checkpoint(task.id, "Before repair")
            self._record(task.id, "Repair checkpoint created", f"checkpoint:{checkpoint.id}")

            self._record(task.id, "Minimal repair applied", repair())
            self._require_stage(task.id, "Verification passed", verify())
            self._require_stage(task.id, "Red-team check passed", red_team())
            self._require_stage(task.id, "Regression check passed", regression())
        except Exception as exc:
            task.fail(str(exc))
            raise

        task.succeed("Alpha workflow verified")
        return AlphaWorkflowResult(task=task, checkpoint_id=checkpoint.id)

    def _record(self, task_id: str, claim: str, details: str) -> None:
        self.orchestrator.evidence.record(
            Evidence(
                claim=claim,
                source=f"alpha:{task_id}",
                verification_status=VerificationStatus.VERIFIED,
                details=details,
            )
        )

    def _require_stage(self, task_id: str, claim: str, passed: bool) -> None:
        if not passed:
            self.orchestrator.evidence.record(
                Evidence(
                    claim=claim,
                    source=f"alpha:{task_id}",
                    verification_status=VerificationStatus.FAILED,
                    details="stage returned false",
                )
            )
            raise RuntimeError(claim)
        self._record(task_id, claim, "stage returned true")
