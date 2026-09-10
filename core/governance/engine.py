"""Single governance decision point for policy gates."""

from core.governance.cost import CostPolicy
from core.governance.data_policy import DataPolicy
from core.governance.legal import LegalPolicy
from core.governance.models import Decision, DecisionStatus, GovernanceRequest
from core.governance.risk import RiskClassifier
from core.governance.security import SecurityPolicy


class GovernanceEngine:
    """Evaluate a request across independent policy domains, failing closed."""

    def __init__(self) -> None:
        self.security = SecurityPolicy()
        self.legal = LegalPolicy()
        self.cost = CostPolicy()
        self.data = DataPolicy()
        self.risk = RiskClassifier()

    def decide(self, request: GovernanceRequest) -> Decision:
        reasons = [
            *self.security.evaluate(request),
            *self.legal.evaluate(request),
            *self.cost.evaluate(request),
            *self.data.evaluate(request),
        ]
        derived_risk = self.risk.classify(request)
        if derived_risk.value != request.risk.value:
            reasons.append(f"derived risk is {derived_risk.value}")
        if any("denied" in reason for reason in reasons):
            status = DecisionStatus.DENY
        elif reasons:
            status = DecisionStatus.APPROVAL_REQUIRED
        else:
            status = DecisionStatus.ALLOW
        return Decision(status=status, reasons=tuple(reasons), request=request)
