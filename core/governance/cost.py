"""Cost controls that prevent silent paid-resource usage."""

from core.governance.models import GovernanceRequest


class CostPolicy:
    """Enforce free-first routing and explicit approval for paid resources."""

    def evaluate(self, request: GovernanceRequest) -> list[str]:
        if request.estimated_cost < 0:
            return ["negative cost estimate is invalid"]
        if request.paid_resource and request.approval is None:
            return ["paid resource requires explicit approval"]
        return []
