"""Fail-closed identity, authorization, egress, secret and audit contracts."""
from __future__ import annotations

import base64
import hashlib
import hmac
import ipaddress
import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Iterable
from urllib.parse import urlparse


class SecurityError(ValueError):
    """Base security contract error."""


class Decision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    APPROVAL_REQUIRED = "approval_required"


@dataclass(frozen=True)
class Identity:
    subject: str
    tenant: str
    roles: tuple[str, ...] = ()
    authenticated: bool = True

    def __post_init__(self) -> None:
        if not self.subject.strip() or not self.tenant.strip():
            raise SecurityError("identity requires subject and tenant")
        if any(not role.strip() for role in self.roles):
            raise SecurityError("identity roles must not be empty")


@dataclass(frozen=True)
class PermissionGrant:
    subject: str
    tenant: str
    action: str
    resource: str
    scope: str
    expires_at: datetime | None = None
    require_approval: bool = False

    def __post_init__(self) -> None:
        if not all(v.strip() for v in (self.subject, self.tenant, self.action, self.resource, self.scope)):
            raise SecurityError("permission grant requires subject/tenant/action/resource/scope")
        if self.expires_at is not None and self.expires_at.tzinfo is None:
            raise SecurityError("grant expiry must be timezone-aware")

    def active(self) -> bool:
        return self.expires_at is None or self.expires_at > datetime.now(UTC)


@dataclass(frozen=True)
class SecurityToken:
    token: str
    subject: str
    action: str
    resource: str
    scope: str
    expires_at: datetime
    policy_version: str


@dataclass(frozen=True)
class AuthorizationRequest:
    identity: Identity
    action: str
    resource: str
    scope: str
    risk: str = "low"
    destructive: bool = False
    external_egress: bool = False
    network_target: str = ""
    credential_access: bool = False
    tool_name: str = ""
    approval: str | None = None
    input_text: str = ""

    def __post_init__(self) -> None:
        if not all(v.strip() for v in (self.action, self.resource, self.scope)):
            raise SecurityError("authorization requires action/resource/scope")


@dataclass(frozen=True)
class AuthorizationResult:
    decision: Decision
    reasons: tuple[str, ...]
    policy_version: str
    evidence_id: str

    @property
    def allowed(self) -> bool:
        return self.decision is Decision.ALLOW


@dataclass(frozen=True)
class EgressPolicy:
    allowed_hosts: tuple[str, ...] = ()
    allowed_schemes: tuple[str, ...] = ("https",)
    allow_private_addresses: bool = False

    def permits(self, target: str) -> bool:
        try:
            parsed = urlparse(target)
            scheme = parsed.scheme.lower()
            host = (parsed.hostname or "").lower().rstrip(".")
            address = ipaddress.ip_address(host) if host else None
        except ValueError:
            return False
        if scheme not in {s.lower() for s in self.allowed_schemes} or not host:
            return False
        if address is not None and not self.allow_private_addresses and (
            address.is_private or address.is_loopback or address.is_link_local or address.is_reserved
        ):
            return False
        return host in {h.lower().rstrip(".") for h in self.allowed_hosts}


@dataclass(frozen=True)
class TrustBoundary:
    source: str
    destination: str
    allowed: bool = False
    reason: str = ""

    def __post_init__(self) -> None:
        if not self.source.strip() or not self.destination.strip():
            raise SecurityError("trust boundary requires source and destination")
        if self.allowed and not self.reason.strip():
            raise SecurityError("allowed trust boundary requires justification")


@dataclass(frozen=True)
class PolicyVersion:
    version: str
    digest: str
    active: bool = True


@dataclass(frozen=True)
class AuditEvent:
    evidence_id: str
    subject: str
    action: str
    resource: str
    decision: Decision
    policy_version: str
    reasons: tuple[str, ...]
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class SecretScanner:
    """Detect and redact common credential forms."""

    _PATTERNS = (
        re.compile(r"(?i)bearer\s+[A-Za-z0-9._~+/=-]{12,}"),
        re.compile(r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*[^\s,;]+"),
        re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]+?-----END [A-Z ]*PRIVATE KEY-----"),
        re.compile(r"\b(?:sk|rk)-[A-Za-z0-9_-]{16,}\b"),
    )

    @classmethod
    def contains_secret(cls, text: str) -> bool:
        return any(p.search(text) for p in cls._PATTERNS)

    @classmethod
    def redact(cls, text: str) -> str:
        for pattern in cls._PATTERNS:
            text = pattern.sub("[REDACTED]", text)
        return text


class InjectionScanner:
    """Conservative prompt/tool injection detector."""

    _PATTERNS = (
        re.compile(r"(?i)ignore\s+(?:all|any|the)\s+(?:previous|prior|above)\s+instructions"),
        re.compile(r"(?i)(?:reveal|print|show|dump)\s+(?:the\s+)?(?:system|developer)\s+(?:prompt|instructions)"),
        re.compile(r"(?i)disable\s+(?:security|safety|authorization|policy)"),
        re.compile(r"(?i)you\s+are\s+now\s+(?:the\s+)?(?:system|developer|admin)"),
        re.compile(r"(?i)override\s+(?:policy|permission|approval|security)"),
    )

    @classmethod
    def contains_injection(cls, text: str) -> bool:
        return any(p.search(text) for p in cls._PATTERNS)


class SecurityPolicy:
    """Versioned, deny-by-default policy authority."""

    def __init__(self, grants: Iterable[PermissionGrant] = (), *, policy_version: str = "v1", egress: EgressPolicy | None = None, boundaries: Iterable[TrustBoundary] = (), approval_risks: Iterable[str] = ("high", "critical")) -> None:
        self._grants = tuple(grants)
        self.version = PolicyVersion(policy_version, hashlib.sha256(policy_version.encode()).hexdigest())
        self.egress = egress or EgressPolicy()
        self._boundaries = tuple(boundaries)
        self._approval_risks = frozenset(approval_risks)

    @staticmethod
    def _scope_matches(granted: str, requested: str) -> bool:
        return granted == requested or (granted.endswith("/*") and requested.startswith(granted[:-1]))

    def _grant(self, request: AuthorizationRequest) -> PermissionGrant | None:
        return next((g for g in self._grants if g.active() and g.subject == request.identity.subject and g.tenant == request.identity.tenant and g.action == request.action and g.resource == request.resource and self._scope_matches(g.scope, request.scope)), None)

    def evaluate(self, request: AuthorizationRequest) -> tuple[Decision, tuple[str, ...]]:
        reasons: list[str] = []
        if not self.version.active:
            reasons.append("security policy version is inactive")
        if not request.identity.authenticated:
            reasons.append("unauthenticated identity")
        if not request.identity.tenant.strip():
            reasons.append("missing tenant isolation")
        if SecretScanner.contains_secret(request.input_text):
            reasons.append("secret-like input rejected")
        if InjectionScanner.contains_injection(request.input_text):
            reasons.append("prompt or tool injection rejected")
        if request.external_egress and not self.egress.permits(request.network_target):
            reasons.append("egress target is not allowlisted")
        if request.credential_access and request.approval is None:
            reasons.append("credential access requires approval")
        if request.destructive and request.approval is None:
            reasons.append("destructive operation requires approval")
        if request.risk.lower() in self._approval_risks and request.approval is None:
            reasons.append("high-risk operation requires approval")
        if request.external_egress and request.credential_access:
            reasons.append("credential-bearing external egress is denied")
        if request.resource.startswith("external:") and not any(b.source == request.identity.tenant and b.destination == request.resource and b.allowed for b in self._boundaries):
            reasons.append("trust boundary is not explicitly allowed")
        if self._grant(request) is None:
            reasons.append("no active least-privilege grant")
        deny_markers = ("denied", "rejected", "no active", "not allowlisted", "not explicitly", "unauthenticated", "missing tenant", "inactive")
        if any(any(marker in reason for marker in deny_markers) for reason in reasons):
            return Decision.DENY, tuple(reasons)
        if reasons:
            return Decision.APPROVAL_REQUIRED, tuple(reasons)
        return Decision.ALLOW, ()


class SecurityPlatform:
    """Security authority for authorization decisions and non-secret evidence."""

    def __init__(self, policy: SecurityPolicy, signing_key: bytes) -> None:
        if not signing_key:
            raise SecurityError("signing key must not be empty")
        self.policy = policy
        self._signing_key = bytes(signing_key)
        self._audit: list[AuditEvent] = []
        self._used_tokens: set[str] = set()

    @staticmethod
    def _evidence_id(request: AuthorizationRequest, decision: Decision, version: str) -> str:
        material = "|".join((request.identity.subject, request.identity.tenant, request.action, request.resource, request.scope, decision.value, version))
        return hashlib.sha256(material.encode()).hexdigest()[:24]

    def authorize(self, request: AuthorizationRequest) -> AuthorizationResult:
        decision, reasons = self.policy.evaluate(request)
        evidence_id = self._evidence_id(request, decision, self.policy.version.version)
        safe_reasons = tuple(SecretScanner.redact(r) for r in reasons)
        self._audit.append(AuditEvent(evidence_id, request.identity.subject, request.action, request.resource, decision, self.policy.version.version, safe_reasons))
        return AuthorizationResult(decision, safe_reasons, self.policy.version.version, evidence_id)

    def issue_token(self, request: AuthorizationRequest, ttl_seconds: int = 300) -> SecurityToken:
        if ttl_seconds <= 0 or ttl_seconds > 3600:
            raise SecurityError("token TTL must be between 1 and 3600 seconds")
        if not self.authorize(request).allowed:
            raise SecurityError("authorization did not allow token issuance")
        expires = int(datetime.now(UTC).timestamp()) + ttl_seconds
        payload = {"sub": request.identity.subject, "tenant": request.identity.tenant, "act": request.action, "res": request.resource, "scope": request.scope, "exp": expires, "pol": self.policy.version.version}
        encoded = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()).decode().rstrip("=")
        signature = hmac.new(self._signing_key, encoded.encode(), hashlib.sha256).hexdigest()
        return SecurityToken(f"{encoded}.{signature}", request.identity.subject, request.action, request.resource, request.scope, datetime.fromtimestamp(expires, UTC), self.policy.version.version)

    def consume_token(self, token: str, request: AuthorizationRequest) -> bool:
        if not token or token in self._used_tokens or "." not in token:
            return False
        encoded, signature = token.rsplit(".", 1)
        if not hmac.compare_digest(signature, hmac.new(self._signing_key, encoded.encode(), hashlib.sha256).hexdigest()):
            return False
        try:
            payload = json.loads(base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)))
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
            return False
        if not self.policy.version.active or payload.get("pol") != self.policy.version.version:
            return False
        if int(payload.get("exp", 0)) <= int(datetime.now(UTC).timestamp()):
            return False
        bound = (("sub", request.identity.subject), ("tenant", request.identity.tenant), ("act", request.action), ("res", request.resource), ("scope", request.scope))
        if any(payload.get(k) != v for k, v in bound):
            return False
        self._used_tokens.add(token)
        return True

    def audit(self) -> tuple[AuditEvent, ...]:
        return tuple(self._audit)
