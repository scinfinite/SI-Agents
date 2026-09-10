"""Typed security and governance contracts."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from types import MappingProxyType
from typing import Mapping
from uuid import uuid4


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


class GovernanceDecision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    APPROVAL_REQUIRED = "approval_required"


@dataclass(frozen=True)
class Approval:
    approved_by: str
    reason: str
    reference: str | None = None
    expires_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.approved_by.strip() or not self.reason.strip():
            raise ValueError("approval requires approver and reason")
        if self.expires_at is not None and self.expires_at.tzinfo is None:
            raise ValueError("approval expiry must be timezone-aware")

    def active(self, now: datetime | None = None) -> bool:
        return self.expires_at is None or self.expires_at > (now or datetime.now(UTC))


@dataclass(frozen=True)
class Capability:
    name: str
    description: str = ""
    risk: RiskLevel = RiskLevel.LOW

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("capability name must not be empty")


@dataclass(frozen=True)
class Permission:
    subject: str
    capability: str
    scope: str = ""
    effect: GovernanceDecision = GovernanceDecision.ALLOW
    conditions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.subject.strip() or not self.capability.strip():
            raise ValueError("permission requires subject and capability")
        if self.effect == GovernanceDecision.ALLOW and not self.scope.strip():
            raise ValueError("allow permissions require an explicit scope")


@dataclass(frozen=True)
class Policy:
    name: str
    description: str
    deny_capabilities: tuple[str, ...] = ()
    approval_risks: tuple[RiskLevel, ...] = (RiskLevel.HIGH, RiskLevel.CRITICAL)
    max_cost: float | None = None
    allow_external_egress: bool = False

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.description.strip():
            raise ValueError("policy requires name and description")
        if self.max_cost is not None and self.max_cost < 0:
            raise ValueError("policy max_cost must be non-negative")


@dataclass(frozen=True)
class Risk:
    level: RiskLevel
    rationale: str
    factors: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.rationale.strip():
            raise ValueError("risk rationale must not be empty")


@dataclass(frozen=True)
class TrustBoundary:
    name: str
    source: str
    destination: str
    allowed: bool = False
    justification: str = ""

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.source.strip() or not self.destination.strip():
            raise ValueError("trust boundary requires name, source, and destination")
        if self.allowed and not self.justification.strip():
            raise ValueError("allowed trust boundaries require justification")


@dataclass(frozen=True)
class CredentialReference:
    name: str
    provider: str
    secret_ref: str
    allowed_scopes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not all(item.strip() for item in (self.name, self.provider, self.secret_ref)):
            raise ValueError("credential reference fields must not be empty")
        if not self.allowed_scopes:
            raise ValueError("credential reference requires explicit scopes")


@dataclass(frozen=True)
class DataClassification:
    resource: str
    classification: DataClass
    owner: str
    retention: str = ""

    def __post_init__(self) -> None:
        if not all(item.strip() for item in (self.resource, self.owner)):
            raise ValueError("data classification requires resource and owner")


@dataclass(frozen=True)
class CostConstraint:
    name: str
    max_cost: float
    currency: str = "USD"
    period: str = "request"

    def __post_init__(self) -> None:
        if not self.name.strip() or self.max_cost < 0 or not self.currency.strip() or not self.period.strip():
            raise ValueError("invalid cost constraint")


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
    capabilities: tuple[str, ...] = ()
    subject: str = ""
    metadata: Mapping[str, str] = field(default_factory=dict)
    request_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.action.strip():
            raise ValueError("action must not be empty")
        if self.estimated_cost < 0:
            raise ValueError("estimated_cost must be non-negative")
        if not self.provenance:
            raise ValueError("governance request requires provenance")
        if any(not item.strip() for item in self.capabilities):
            raise ValueError("capability names must not be empty")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


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
