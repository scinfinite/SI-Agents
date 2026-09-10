"""Risk classification derived from requested effects."""

from core.governance.models import GovernanceRequest, RiskLevel


class RiskClassifier:
    """Derive a conservative minimum risk level from action properties."""

    def classify(self, request: GovernanceRequest) -> RiskLevel:
        if request.credential or request.production and request.destructive:
            return RiskLevel.CRITICAL
        if request.destructive or request.production or request.external_egress:
            return max_risk(RiskLevel.HIGH, request.risk)
        if request.paid_resource or request.legal_review_required:
            return max_risk(RiskLevel.MEDIUM, request.risk)
        return request.risk


def max_risk(left: RiskLevel, right: RiskLevel) -> RiskLevel:
    order = {
        RiskLevel.LOW: 0,
        RiskLevel.MEDIUM: 1,
        RiskLevel.HIGH: 2,
        RiskLevel.CRITICAL: 3,
    }
    return left if order[left] >= order[right] else right
