import pytest

from core.orchestrator.alpha_workflow import AlphaWorkflow
from core.orchestrator.orchestrator import Orchestrator
from core.state.task_state import TaskStatus


def test_alpha_workflow_enforces_repair_verification_order() -> None:
    orchestrator = Orchestrator()
    workflow = AlphaWorkflow(orchestrator)
    stages: list[str] = []

    result = workflow.run(
        "repair fixture",
        inspect=lambda: stages.append("inspect") or "fixture inspected",
        reproduce=lambda: stages.append("reproduce") or True,
        repair=lambda: stages.append("repair") or "minimal fix",
        verify=lambda: stages.append("verify") or True,
        red_team=lambda: stages.append("red_team") or True,
        regression=lambda: stages.append("regression") or True,
    )

    assert stages == ["inspect", "reproduce", "repair", "verify", "red_team", "regression"]
    assert result.task.status is TaskStatus.SUCCEEDED
    assert len(orchestrator.checkpoints.for_task(result.task.id)) == 1
    assert len(orchestrator.evidence.all()) == 7


def test_alpha_workflow_stops_before_repair_when_reproduction_fails() -> None:
    orchestrator = Orchestrator()
    workflow = AlphaWorkflow(orchestrator)
    stages: list[str] = []

    with pytest.raises(RuntimeError, match="Expected failure"):
        workflow.run(
            "cannot reproduce",
            inspect=lambda: stages.append("inspect") or "inspected",
            reproduce=lambda: stages.append("reproduce") or False,
            repair=lambda: stages.append("repair") or "must not run",
            verify=lambda: stages.append("verify") or True,
            red_team=lambda: stages.append("red_team") or True,
            regression=lambda: stages.append("regression") or True,
        )

    assert stages == ["inspect", "reproduce"]
    task = orchestrator.tasks.all()[0]
    assert task.status is TaskStatus.FAILED
    assert orchestrator.checkpoints.for_task(task.id) == ()


def test_alpha_workflow_records_failed_verification() -> None:
    orchestrator = Orchestrator()
    workflow = AlphaWorkflow(orchestrator)

    with pytest.raises(RuntimeError, match="Verification passed"):
        workflow.run(
            "failed verification",
            inspect=lambda: "inspected",
            reproduce=lambda: True,
            repair=lambda: "repaired",
            verify=lambda: False,
            red_team=lambda: True,
            regression=lambda: True,
        )

    failed = [item for item in orchestrator.evidence.all() if item.verification_status.value == "failed"]
    assert len(failed) == 1
    assert failed[0].claim == "Verification passed"
