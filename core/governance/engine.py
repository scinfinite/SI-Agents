"""Single governance decision point for policy gates."""

from core.governance.cost import CostPolicy
from core.governance.data_policy import DataPolicy
from core.governance.legal import LegalPolicy
from core.governance.models import Decision, DecisionStatus, GovernanceRequest
from core.governance.risk import RiskClassifier
from core.governance.security import SecurityPolicy
from core.governance.store import GovernanceStore


class GovernanceEngine:
    """Evaluate a request across independent policy domains, failing closed."""

    def __init__(self, store: GovernanceStore | None = None) -> None:
        self.security = SecurityPolicy()
        self.legal = LegalPolicy()
        self.cost = CostPolicy()
        self.data = DataPolicy()
        self.risk = RiskClassifier()
        self.store = store or GovernanceStore()

    def decide(self, request: GovernanceRequest) -> Decision:
        reasons = [
            *self.security.evaluate(request),
            *self.legal.evaluate(request),
            *self.cost.evaluate(request),
            *self.data.evaluate(request),
        ]
        effective_risk = self.risk.classify(request)

        if request.approval is not None and not request.approval.active():
            reasons.append("approval is expired")

        snapshot = self.store.snapshot()
        for policy in snapshot.policies:
            if any(capability in policy.deny_capabilities for capability in request.capabilities):
                reasons.append(f"policy {policy.name} denies requested capability")
            if request.external_egress and not policy.allow_external_egress:
                reasons.append(f"policy {policy.name} requires approval for external egress")
            if policy.max_cost is not None and request.estimated_cost > policy.max_cost:
                reasons.append(f"policy {policy.name} cost limit exceeded")

        if request.subject and request.capabilities:
            for capability in request.capabilities:
                matches = [
                    item for item in snapshot.permissions
                    if item.subject == request.subject and item.capability == capability
                ]
                if not matches:
                    reasons.append(f"no scoped permission for {request.subject}:{capability}")
                elif not any(item.effect.value == "allow" for item in matches):
                    reasons.append(f"permission denies {request.subject}:{capability}")

        hard_denials = [reason for reason in reasons if "denied" in reason or "no scoped permission" in reason or "permission denies" in reason or "credential-bearing external egress" in reason]
        if hard_denials:
            status = DecisionStatus.DENY
        elif reasons:
            status = DecisionStatus.APPROVAL_REQUIRED
        else:
            status = DecisionStatus.ALLOW
        return Decision(
            status=status,
            reasons=tuple(reasons),
            request=request,
            effective_risk=effective_risk,
        )
