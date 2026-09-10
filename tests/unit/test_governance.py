from core.governance import (
    Approval,
    AuditLog,
    DataClass,
    DecisionStatus,
    GovernanceEngine,
    GovernanceRequest,
    RiskLevel,
)


def test_safe_local_request_is_allowed() -> None:
    request = GovernanceRequest(action="read repository", risk=RiskLevel.LOW)
    decision = GovernanceEngine().decide(request)
    assert decision.status is DecisionStatus.ALLOW


def test_paid_resource_requires_approval() -> None:
    request = GovernanceRequest(action="call provider", risk=RiskLevel.MEDIUM, paid_resource=True)
    assert GovernanceEngine().decide(request).status is DecisionStatus.APPROVAL_REQUIRED


def test_paid_resource_with_approval_is_allowed() -> None:
    request = GovernanceRequest(
        action="call provider", risk=RiskLevel.MEDIUM, paid_resource=True,
        approval=Approval("human", "approved budget", "ticket-1"),
    )
    assert GovernanceEngine().decide(request).status is DecisionStatus.ALLOW


def test_sensitive_egress_without_approval_requires_approval() -> None:
    request = GovernanceRequest(
        action="upload data", risk=RiskLevel.HIGH, data_class=DataClass.SENSITIVE, external_egress=True
    )
    assert GovernanceEngine().decide(request).status is DecisionStatus.APPROVAL_REQUIRED


def test_sensitive_egress_with_approval_is_allowed() -> None:
    request = GovernanceRequest(
        action="upload data", risk=RiskLevel.HIGH, data_class=DataClass.SENSITIVE, external_egress=True,
        approval=Approval("human", "approved transfer"),
    )
    assert GovernanceEngine().decide(request).status is DecisionStatus.ALLOW


def test_confidential_egress_requires_approval() -> None:
    request = GovernanceRequest(
        action="send report", risk=RiskLevel.MEDIUM, data_class=DataClass.CONFIDENTIAL, external_egress=True
    )
    assert GovernanceEngine().decide(request).status is DecisionStatus.APPROVAL_REQUIRED


def test_credential_egress_is_denied_even_with_approval() -> None:
    request = GovernanceRequest(
        action="send secret", risk=RiskLevel.CRITICAL, credential=True, external_egress=True,
        approval=Approval("human", "attempted approval"),
    )
    assert GovernanceEngine().decide(request).status is DecisionStatus.DENY


def test_credential_operation_requires_approval() -> None:
    request = GovernanceRequest(action="rotate credential", risk=RiskLevel.LOW, credential=True)
    decision = GovernanceEngine().decide(request)
    assert decision.status is DecisionStatus.APPROVAL_REQUIRED
    assert decision.effective_risk is RiskLevel.CRITICAL


def test_credential_operation_with_approval_is_allowed() -> None:
    request = GovernanceRequest(
        action="rotate credential", risk=RiskLevel.CRITICAL, credential=True,
        approval=Approval("human", "approved rotation"),
    )
    assert GovernanceEngine().decide(request).status is DecisionStatus.ALLOW


def test_high_risk_destructive_requires_approval() -> None:
    request = GovernanceRequest(action="delete workspace", risk=RiskLevel.HIGH, destructive=True)
    assert GovernanceEngine().decide(request).status is DecisionStatus.APPROVAL_REQUIRED


def test_high_risk_destructive_with_approval_is_allowed() -> None:
    request = GovernanceRequest(
        action="delete workspace", risk=RiskLevel.HIGH, destructive=True,
        approval=Approval("human", "approved deletion"),
    )
    assert GovernanceEngine().decide(request).status is DecisionStatus.ALLOW


def test_publication_without_provenance_requires_review() -> None:
    request = GovernanceRequest(action="publish artifact", risk=RiskLevel.MEDIUM, publication=True)
    assert GovernanceEngine().decide(request).status is DecisionStatus.APPROVAL_REQUIRED


def test_publication_with_provenance_is_allowed() -> None:
    request = GovernanceRequest(
        action="publish artifact", risk=RiskLevel.MEDIUM, publication=True, provenance=("source-a",)
    )
    assert GovernanceEngine().decide(request).status is DecisionStatus.ALLOW


def test_negative_cost_is_invalid() -> None:
    try:
        GovernanceRequest(action="bad estimate", risk=RiskLevel.LOW, estimated_cost=-1)
    except ValueError as exc:
        assert "non-negative" in str(exc)
    else:
        raise AssertionError("negative cost must be rejected")


def test_approval_validation_is_fail_closed() -> None:
    try:
        Approval("", "missing approver")
    except ValueError as exc:
        assert "approver" in str(exc)
    else:
        raise AssertionError("invalid approval must fail")


def test_audit_log_records_summary_only() -> None:
    decision = GovernanceEngine().decide(
        GovernanceRequest(action="read repository", risk=RiskLevel.LOW)
    )
    record = AuditLog().record(decision)
    assert record.action == "read repository"
    assert record.effective_risk == "low"
    assert not hasattr(record, "approval")
