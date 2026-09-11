"""Fail-closed, auditable capability authorization for V4 Phase 50."""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Mapping, Protocol

from core.governance.models import Approval, DecisionStatus, GovernanceDecision, Permission, Policy, RiskLevel


_CONDITION = re.compile(r"^([A-Za-z_][A-Za-z0-9_.-]*)=(.+)$")


class CapabilitySubject(Protocol):
    agent_id: str
    capabilities: tuple[str, ...]


@dataclass(frozen=True)
class AuthorizationRequest:
    """Minimal authorization input; no secret values are accepted."""

    subject: str
    capabilities: tuple[str, ...]
    scope: str
    risk: RiskLevel = RiskLevel.LOW
    metadata: Mapping[str, str] = field(default_factory=dict)
    estimated_cost: float = 0.0
    external_egress: bool = False
    approval: Approval | None = None
    provenance: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.subject.strip() or not self.scope.strip():
            raise ValueError("subject and scope are required")
        if not self.capabilities or any(not item.strip() for item in self.capabilities):
            raise ValueError("at least one non-empty capability is required")
        if len(set(self.capabilities)) != len(self.capabilities):
            raise ValueError("capabilities must be unique")
        if self.estimated_cost < 0:
            raise ValueError("estimated_cost must be non-negative")
        if any(not key.strip() or not value.strip() for key, value in self.metadata.items()):
            raise ValueError("metadata keys and values must not be empty")
        if any(not item.strip() for item in self.provenance):
            raise ValueError("provenance entries must not be empty")

    def fingerprint(self) -> str:
        payload = {
            "subject": self.subject,
            "capabilities": sorted(self.capabilities),
            "scope": self.scope,
            "risk": self.risk.value,
            "metadata": sorted(self.metadata.items()),
            "estimated_cost": self.estimated_cost,
            "external_egress": self.external_egress,
            "provenance": list(self.provenance),
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True)
class AuthorizationEvidence:
    """Safe evidence for audit: identifiers and hashes only, never credentials."""

    request_fingerprint: str
    matched_permissions: tuple[str, ...]
    denied_permissions: tuple[str, ...]
    matched_policies: tuple[str, ...]
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if self.evaluated_at.tzinfo is None:
            raise ValueError("evaluated_at must be timezone-aware")


@dataclass(frozen=True)
class AuthorizationDecision:
    status: DecisionStatus
    reasons: tuple[str, ...]
    evidence: AuthorizationEvidence

    @property
    def allowed(self) -> bool:
        return self.status == DecisionStatus.ALLOW


class CapabilityAuthorizer:
    """Evaluate capability grants with explicit scope, deny precedence and fail-closed defaults."""

    def __init__(self, permissions: tuple[Permission, ...] = (), policies: tuple[Policy, ...] = ()) -> None:
        self._permissions = tuple(permissions)
        self._policies = tuple(policies)
        self._validate_configuration()

    def _validate_configuration(self) -> None:
        for permission in self._permissions:
            if permission.effect == GovernanceDecision.ALLOW and not permission.scope.strip():
                raise ValueError("allow permissions require explicit scope")
        if len({(p.subject, p.capability, p.scope, p.effect, p.conditions) for p in self._permissions}) != len(self._permissions):
            raise ValueError("duplicate permissions are not allowed")
        if len({policy.name for policy in self._policies}) != len(self._policies):
            raise ValueError("policy names must be unique")

    def authorize(self, request: AuthorizationRequest, *, declared_capabilities: tuple[str, ...] | None = None) -> AuthorizationDecision:
        declared = set(declared_capabilities) if declared_capabilities is not None else None
        reasons: list[str] = []
        matched: list[str] = []
        denied: list[str] = []
        policies = [policy for policy in self._policies if policy.deny_capabilities]
        matched_policy_names = tuple(policy.name for policy in policies)

        if declared is not None and not set(request.capabilities).issubset(declared):
            missing = sorted(set(request.capabilities) - declared)
            reasons.append(f"capability not declared by subject: {', '.join(missing)}")
            return self._decision(DecisionStatus.DENY, reasons, matched, denied, matched_policy_names, request)

        for policy in self._policies:
            denied_caps = set(policy.deny_capabilities)
            blocked = sorted(set(request.capabilities) & denied_caps)
            if blocked:
                reasons.append(f"policy {policy.name} denies: {', '.join(blocked)}")
            if request.external_egress and not policy.allow_external_egress:
                reasons.append(f"policy {policy.name} denies external egress")
            if policy.max_cost is not None and request.estimated_cost > policy.max_cost:
                reasons.append(f"policy {policy.name} cost limit exceeded")

        for capability in request.capabilities:
            cap_permissions = [
                permission for permission in self._permissions
                if permission.subject == request.subject and permission.capability == capability
            ]
            explicit_denies = [permission for permission in cap_permissions if permission.effect == GovernanceDecision.DENY and self._conditions_match(permission, request.metadata)]
            if explicit_denies:
                denied.extend(self._permission_id(permission) for permission in explicit_denies)
                reasons.append(f"explicit deny for {capability}")
                continue
            grants = [
                permission for permission in cap_permissions
                if permission.effect == GovernanceDecision.ALLOW
                and self._scope_matches(permission.scope, request.scope)
                and self._conditions_match(permission, request.metadata)
            ]
            if grants:
                matched.extend(self._permission_id(permission) for permission in grants)
            else:
                reasons.append(f"no matching grant for {capability} in scope {request.scope}")

        if reasons:
            return self._decision(DecisionStatus.DENY, reasons, matched, denied, matched_policy_names, request)

        approval_required = any(request.risk in policy.approval_risks for policy in self._policies)
        if approval_required and (request.approval is None or not request.approval.active()):
            return self._decision(DecisionStatus.APPROVAL_REQUIRED, ["active approval required by risk policy"], matched, denied, matched_policy_names, request)

        return self._decision(DecisionStatus.ALLOW, ["all requested capabilities have explicit matching grants"], matched, denied, matched_policy_names, request)

    def authorize_subject(self, subject: CapabilitySubject, request: AuthorizationRequest) -> AuthorizationDecision:
        if request.subject != subject.agent_id:
            return self._decision(
                DecisionStatus.DENY,
                ["request subject does not match declared agent subject"],
                (), (), (), request,
            )
        return self.authorize(request, declared_capabilities=subject.capabilities)

    @staticmethod
    def _scope_matches(grant: str, requested: str) -> bool:
        if not grant or not requested:
            return False
        if grant == requested:
            return True
        if grant.endswith("/*"):
            prefix = grant[:-2].rstrip("/")
            return requested.startswith(prefix + "/")
        return False

    @staticmethod
    def _conditions_match(permission: Permission, metadata: Mapping[str, str]) -> bool:
        for condition in permission.conditions:
            match = _CONDITION.fullmatch(condition.strip())
            if match is None or metadata.get(match.group(1)) != match.group(2):
                return False
        return True

    @staticmethod
    def _permission_id(permission: Permission) -> str:
        raw = "|".join((permission.subject, permission.capability, permission.scope, permission.effect.value, *permission.conditions))
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    @staticmethod
    def _decision(status: DecisionStatus, reasons: list[str], matched: list[str] | tuple[str, ...], denied: list[str] | tuple[str, ...], policies: tuple[str, ...], request: AuthorizationRequest) -> AuthorizationDecision:
        evidence = AuthorizationEvidence(request.fingerprint(), tuple(sorted(set(matched))), tuple(sorted(set(denied))), policies)
        return AuthorizationDecision(status, tuple(reasons), evidence)


__all__ = ["AuthorizationDecision", "AuthorizationEvidence", "AuthorizationRequest", "CapabilityAuthorizer", "CapabilitySubject"]
