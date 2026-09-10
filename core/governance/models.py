"""Typed governance requests and auditable decisions."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DataClass(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    SENSITIVE = "sensitive"


class DecisionStatus(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    APPROVAL_REQUIRED = "approval_required"


@dataclass(frozen=True)
class Approval:
    approved_by: str
    reason: str
    reference: str | None = None

    def __post_init__(self) -> None:
        if not self.approved_by.strip() or not self.reason.strip():
            raise ValueError("approval requires approver and reason")


@dataclass(frozen=True)
class GovernanceRequest:
    action: str
    risk: RiskLevel
    data_class: DataClass = DataClass.PUBLIC
    external_egress: bool = False
    paid_resource: bool = False
    destructive: bool = False
    production: bool = False
    credential: bool = False
    publication: bool = False
    legal_review_required: bool = False
    estimated_cost: float = 0.0
    approval: Approval | None = None
    provenance: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.action.strip():
            raise ValueError("action must not be empty")
        if self.estimated_cost < 0:
            raise ValueError("estimated_cost must be non-negative")


@dataclass(frozen=True)
class Decision:
    status: DecisionStatus
    reasons: tuple[str, ...]
    request: GovernanceRequest
    effective_risk: RiskLevel
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def allowed(self) -> bool:
        return self.status == DecisionStatus.ALLOW
