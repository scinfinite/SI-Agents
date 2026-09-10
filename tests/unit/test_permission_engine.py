import pytest

from core.policies.permission_engine import PermissionDenied, PermissionDecision, PermissionEngine


def test_unknown_capability_is_denied() -> None:
    assert PermissionEngine().decide("unknown_action") is PermissionDecision.DENY


def test_local_command_is_allowed_by_default_policy() -> None:
    assert PermissionEngine().decide("local_command") is PermissionDecision.ALLOW


def test_repository_write_is_denied() -> None:
    assert PermissionEngine().decide("repository_write") is PermissionDecision.DENY
    with pytest.raises(PermissionDenied):
        PermissionEngine().require("repository_write")


def test_high_risk_action_requires_approval() -> None:
    engine = PermissionEngine()
    assert engine.decide("paid_resource") is PermissionDecision.APPROVAL_REQUIRED
    assert engine.decide("paid_resource", approval_granted=True) is PermissionDecision.ALLOW


def test_destructive_command_is_denied_even_when_local_commands_are_allowed() -> None:
    engine = PermissionEngine()
    assert engine.decide("local_command") is PermissionDecision.ALLOW
    assert engine.decide("destructive_command") is PermissionDecision.DENY
