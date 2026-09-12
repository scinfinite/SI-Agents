from pathlib import Path

import pytest

from core.automation.workflow_io import export_definition, import_definition
from core.automation.workflows import WorkflowDefinition, WorkflowStep, WorkflowStepKind, WorkflowTrigger, TriggerKind


def test_round_trip_is_canonical_and_preserves_fingerprint(tmp_path: Path) -> None:
    definition = WorkflowDefinition(
        "release",
        2,
        "Release",
        (
            WorkflowStep("build", WorkflowStepKind.TASK, action="build"),
            WorkflowStep("gate", WorkflowStepKind.HUMAN, approval_key="approved", depends_on=("build",)),
        ),
        (WorkflowTrigger(TriggerKind.WEBHOOK, "release-hook"),),
        max_runtime_seconds=3600,
    )
    path = tmp_path / "release.json"
    encoded = export_definition(definition, path)
    restored = import_definition(encoded)
    assert restored.as_dict() == definition.as_dict()
    assert restored.fingerprint() == definition.fingerprint()
    assert import_definition(path).fingerprint() == definition.fingerprint()


def test_import_rejects_invalid_or_oversized_definitions() -> None:
    with pytest.raises(ValueError):
        import_definition("[]")
    with pytest.raises(ValueError):
        import_definition("{" + "x" * (256 * 1024) + "}")
