"""Data classification and egress controls."""

from core.governance.models import DataClass, GovernanceRequest


class DataPolicy:
    """Conservative data-egress rules; sensitive data is never implicitly exported."""

    def evaluate(self, request: GovernanceRequest) -> list[str]:
        if not request.external_egress or request.approval is not None:
            return []
        if request.data_class == DataClass.SENSITIVE:
            return ["sensitive data cannot leave the trust boundary without approval"]
        if request.data_class == DataClass.CONFIDENTIAL:
            return ["confidential external egress requires approval"]
        return []
