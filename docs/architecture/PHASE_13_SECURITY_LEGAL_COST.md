# Phase 13 — Security, Legal + Cost Governance

## Status

**Complete — final Phase 13 head CI is green.**

## Purpose

Phase 13 turns the repository's security, legal/compliance, cost, data-egress, permission, and approval rules into executable governance primitives. Governance is a decision layer: it evaluates an action and returns an auditable allow, deny, or approval-required result. It does not execute the requested action.

## Acceptance criteria

- Security-sensitive actions are evaluated fail-closed.
- Credential-bearing external egress is denied, including when a caller supplies an approval.
- Sensitive and confidential external egress requires explicit approval.
- Destructive/high-risk actions require explicit approval.
- Paid resources require explicit approval and cannot be silently introduced.
- Publication without provenance requires review.
- Risk is conservatively derived from requested effects and recorded separately from the caller's requested risk.
- Decisions contain reasons, timestamps, and the effective risk.
- Governance audit records retain decision evidence without storing request payloads or credentials.
- Policy configuration expresses the security, permission, compliance, and free-first cost boundaries.
- Adversarial unit tests cover denied, approval-required, approved, invalid-input, and provenance paths.

## Architecture

```text
GovernanceRequest
       |
       v
+-------------------+
| GovernanceEngine  |
+-------------------+
 |   |   |   |   |
 v   v   v   v   v
Sec Legal Cost Data Risk
       |
       v
 Decision + AuditLog
```

### Security

`SecurityPolicy` blocks credential-bearing external egress and requires approval for credential operations, high-risk destructive/production operations, and sensitive egress.

### Legal/provenance

`LegalPolicy` requires review where explicitly required and prevents publication without provenance. The system is not legal advice; repository policies identify review points rather than determining jurisdiction-specific legal outcomes.

### Cost

`CostPolicy` implements the free-first principle at the governance boundary: paid resources need explicit approval. Cost estimates are validated as non-negative. Provider selection/routing remains a later Phase 14 concern.

### Data

`DataPolicy` classifies information as public, internal, confidential, or sensitive. Confidential and sensitive external egress is never implicit.

### Risk

`RiskClassifier` derives a conservative effective risk from action properties. Credential operations and destructive production operations are critical; destructive, production, or external-egress actions are at least high risk.

### Audit

`AuditLog` stores immutable decision summaries. It deliberately excludes arbitrary request payloads so governance logging does not become a secret-storage mechanism.

## Boundaries

- Governance does not execute tools or modify repositories.
- An approval does not override the credential-egress deny rule.
- Governance policy is not legal advice.
- Configuration is policy intent; enforcement occurs in the Python governance engine.
- Cost routing across models/providers is deferred to Phase 14.
- Persistent/encrypted audit storage and retention controls are deferred to later hardening.
- No secret material belongs in requests, audit records, tests, or configuration.

## Verification evidence

- Final verified commit: `269b9f1c6cc609602fb6561aec98b3449fd919fb`.
- GitHub Actions CI run: **#339**, run ID `34444191826`.
- Final job: `test`, job ID `102765318224`, completed with **success**.
- Build distributions: success.
- Ruff: `All checks passed!`.
- Tests: **193 passed in 1.34s**.
- All workflow steps completed successfully.
