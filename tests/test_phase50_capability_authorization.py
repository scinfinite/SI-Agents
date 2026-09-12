from datetime import UTC, datetime, timedelta

import pytest

from agents.builder import AgentDefinition
from core.governance.authorization import AuthorizationRequest, CapabilityAuthorizer
from core.governance.models import Approval, GovernanceDecision, Permission, Policy, RiskLevel


def allow(subject: str, capability: str, scope: str, conditions: tuple[str, ...] = ()) -> Permission:
    return Permission(subject, capability, scope, GovernanceDecision.ALLOW, conditions)


def deny(subject: str, capability: str) -> Permission:
    return Permission(subject, capability, "", GovernanceDecision.DENY)


def request(**kwargs):
    defaults = {"subject": "agent-a", "capabilities": ("repo.read",), "scope": "repo/project"}
    defaults.update(kwargs)
    return AuthorizationRequest(**defaults)


def test_explicit_grant_and_scoped_descendant_are_allowed():
    authorizer = CapabilityAuthorizer((allow("agent-a", "repo.read", "repo/*"),))
    decision = authorizer.authorize(request(scope="repo/project/src"))
    assert decision.allowed
    assert decision.evidence.matched_permissions
    assert len(decision.evidence.request_fingerprint) == 64


def test_missing_grant_and_scope_escalation_fail_closed():
    authorizer = CapabilityAuthorizer((allow("agent-a", "repo.read", "repo/project"),))
    assert not authorizer.authorize(request(scope="repo/other")).allowed
    assert not authorizer.authorize(request(capabilities=("repo.write",))).allowed


def test_explicit_deny_overrides_allow():
    authorizer = CapabilityAuthorizer((allow("agent-a", "repo.write", "repo/*"), deny("agent-a", "repo.write")))
    decision = authorizer.authorize(request(capabilities=("repo.write",), scope="repo/project"))
    assert not decision.allowed
    assert any("explicit deny" in reason for reason in decision.reasons)
    assert decision.evidence.denied_permissions


def test_conditions_are_fail_closed():
    authorizer = CapabilityAuthorizer((allow("agent-a", "repo.read", "repo/*", ("environment=dev",)),))
    assert authorizer.authorize(request(metadata={"environment": "dev"})).allowed
    assert not authorizer.authorize(request(metadata={"environment": "prod"})).allowed
    assert not authorizer.authorize(request(metadata={})).allowed


def test_declared_agent_capabilities_cannot_be_bypassed():
    agent = AgentDefinition("agent-a", "reader", "Read only", capabilities=("repo.read",))
    authorizer = CapabilityAuthorizer((allow("agent-a", "repo.read", "repo/*"), allow("agent-a", "repo.write", "repo/*")))
    assert authorizer.authorize_subject(agent, request(capabilities=("repo.read",))).allowed
    decision = authorizer.authorize_subject(agent, request(capabilities=("repo.write",)))
    assert not decision.allowed
    assert any("not declared" in reason for reason in decision.reasons)


def test_subject_identity_is_bound_to_declaration():
    agent = AgentDefinition("agent-a", "reader", "Read only", capabilities=("repo.read",))
    authorizer = CapabilityAuthorizer((allow("agent-a", "repo.read", "repo/*"),))
    decision = authorizer.authorize_subject(agent, request(subject="attacker"))
    assert not decision.allowed
    assert "does not match" in decision.reasons[0]


def test_high_risk_requires_active_request_bound_approval_and_expired_approval_denies():
    authorizer = CapabilityAuthorizer((allow("agent-a", "repo.read", "repo/*"),))
    high = request(risk=RiskLevel.HIGH)
    assert authorizer.authorize(high).status.value == "approval_required"
    expired = Approval("operator", "approved", expires_at=datetime.now(UTC) - timedelta(seconds=1), reference=high.fingerprint())
    assert authorizer.authorize(AuthorizationRequest(**{**high.__dict__, "approval": expired})).status.value == "approval_required"
    active_unbound = Approval("operator", "approved", expires_at=datetime.now(UTC) + timedelta(minutes=5))
    assert authorizer.authorize(AuthorizationRequest(**{**high.__dict__, "approval": active_unbound})).status.value == "approval_required"
    active = Approval("operator", "approved", expires_at=datetime.now(UTC) + timedelta(minutes=5), reference=high.fingerprint())
    assert authorizer.authorize(AuthorizationRequest(**{**high.__dict__, "approval": active})).allowed


def test_approval_cannot_be_replayed_for_modified_request():
    authorizer = CapabilityAuthorizer((allow("agent-a", "repo.read", "repo/*"),))
    original = request(risk=RiskLevel.HIGH)
    approval = Approval("operator", "approved", reference=original.fingerprint())
    modified = request(risk=RiskLevel.HIGH, scope="repo/other", approval=approval)
    decision = authorizer.authorize(modified)
    assert decision.status.value == "approval_required"
    assert "not bound" in decision.reasons[0]


def test_external_egress_requires_explicit_policy_without_overconstraining_unrelated_policies():
    authorizer = CapabilityAuthorizer((allow("agent-a", "net.fetch", "net/*"),), (Policy("audit", "audit"),))
    assert not authorizer.authorize(request(capabilities=("net.fetch",), scope="net/api", external_egress=True)).allowed
    policy = Policy("egress", "explicit egress", allow_external_egress=True)
    assert authorizer.__class__((allow("agent-a", "net.fetch", "net/*"),), (Policy("audit", "audit"), policy)).authorize(
        request(capabilities=("net.fetch",), scope="net/api", external_egress=True)
    ).allowed


def test_cost_policy_is_enforced_without_leaking_request_data():
    policy = Policy("budget", "small budget", max_cost=1.0)
    authorizer = CapabilityAuthorizer((allow("agent-a", "repo.read", "repo/*"),), (policy,))
    decision = authorizer.authorize(request(estimated_cost=2.0))
    assert not decision.allowed
    assert decision.evidence.request_fingerprint not in str(decision.reasons)


def test_secret_like_metadata_is_rejected_before_authorization():
    with pytest.raises(ValueError, match="secret-like"):
        request(metadata={"api_key": "should-never-enter-governance"})


def test_duplicate_permission_configuration_is_rejected():
    permission = allow("agent-a", "repo.read", "repo/*")
    with pytest.raises(ValueError, match="duplicate permissions"):
        CapabilityAuthorizer((permission, permission))
