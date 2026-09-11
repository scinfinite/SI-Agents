"""Phase 42 harness deployment planning and boundary tests."""

from pathlib import Path

import pytest

from core.deployment_center.api import create, snapshot
from core.deployment_center.models import DeploymentState
from core.deployment_center.service import DeploymentCenter


ROOT = Path(__file__).resolve().parents[1]


def test_registered_targets_are_deterministic() -> None:
    center = DeploymentCenter(ROOT)
    targets = center.targets()
    assert [target.id for target in targets] == sorted(target.id for target in targets)
    assert "opencode" in {target.id for target in targets}


def test_valid_plan_is_planning_only() -> None:
    center = DeploymentCenter(ROOT)
    plan = center.plan("p1", "opencode", ("agent-a",), ("team-a",), ("skill-a",))
    assert plan.state is DeploymentState.VALID
    assert center.get("p1") == plan
    assert snapshot(center)["plans"] == [plan.as_dict()]


def test_unknown_target_and_authority_requests_fail_closed() -> None:
    center = DeploymentCenter(ROOT)
    unknown = create(center, {"id": "p2", "harness_id": "missing"})
    assert unknown["state"] == "blocked"
    assert "not registered" in unknown["reasons"][0]
    elevated = create(center, {"id": "p3", "harness_id": "opencode", "capabilities": ["shell"]})
    assert elevated["state"] == "blocked"
    assert "authority" in " ".join(elevated["reasons"])


def test_duplicate_and_blank_identifiers_are_rejected() -> None:
    center = DeploymentCenter(ROOT)
    with pytest.raises(ValueError, match="unique"):
        center.plan("p4", "opencode", ("a", "a"), ())
    with pytest.raises(ValueError, match="empty"):
        center.plan("p5", "opencode", ("",), ())


def test_blocked_plan_cannot_produce_manifest() -> None:
    center = DeploymentCenter(ROOT)
    center.plan("p6", "missing", (), ())
    with pytest.raises(PermissionError, match="not valid"):
        center.manifest("p6")


def test_planning_does_not_enable_or_execute_harness() -> None:
    center = DeploymentCenter(ROOT)
    before = {target.id: target.enabled for target in center.targets()}
    center.plan("p7", "opencode", (), ())
    after = {target.id: target.enabled for target in center.targets()}
    assert after == before
