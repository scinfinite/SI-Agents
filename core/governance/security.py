"""Fail-closed security policy evaluation."""

from core.governance.models import DataClass, GovernanceRequest, RiskLevel


class SecurityPolicy:
    """Evaluate security-sensitive properties without performing the action."""

    def evaluate(self, request: GovernanceRequest) -> list[str]:
        reasons: list[str] = []
        if request.credential and request.external_egress:
            reasons.append("credential-bearing external egress is denied")
        if request.data_class == DataClass.SENSITIVE and request.external_egress and request.approval is None:
            reasons.append("sensitive data external egress requires approval")
        if request.credential and request.approval is None:
            reasons.append("credential operations require approval")
        if request.destructive and request.risk in {RiskLevel.HIGH, RiskLevel.CRITICAL} and request.approval is None:
            reasons.append("high-risk destructive action requires approval")
        if request.production and request.risk in {RiskLevel.HIGH, RiskLevel.CRITICAL} and request.approval is None:
            reasons.append("high-risk production action requires approval")
        return reasons
