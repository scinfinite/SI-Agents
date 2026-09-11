# Phase 50 — Capability Authorization

## Status

**Complete and final-CI verified.**

## Objective

Convert agent/team capability declarations into explicit, fail-closed, auditable authorization decisions without allowing an agent, team, model, provider, or runtime adapter to self-grant authority.

## Delivered

- `AuthorizationRequest` with caller subject, requested capabilities, resource scope, risk, metadata, estimated cost, egress flag, approval and provenance.
- `CapabilityAuthorizer` with exact/descendant scope matching, explicit grants, explicit deny precedence, condition matching, declared-capability enforcement, risk approval gates, cost-policy enforcement, and fail-closed egress policy.
- `AuthorizationDecision` and `AuthorizationEvidence` containing safe identifiers/hashes only; credentials and secret values never enter authorization evidence.
- `authorize_subject()` binds the request subject to the declared agent identity and ensures requested capabilities are declared by that agent.
- Deterministic permission identifiers and request fingerprints support audit correlation without persisting sensitive request contents.
- Existing governance `Permission` and `Policy` primitives remain the policy data model; Phase 50 adds the dedicated admission evaluator rather than creating a competing governance system.
- `core/governance/__init__.py` exports the Phase 50 authorization contracts.

## Security invariants

1. No matching explicit grant means deny.
2. Explicit deny overrides matching allow.
3. A subject cannot request a capability it did not declare.
4. A request cannot authorize under a different subject identity.
5. Scope escalation outside the explicit grant or descendant scope is denied.
6. High/critical-risk requests require active approval.
7. External egress requires an explicit allow policy; absence of policy is deny.
8. Cost limits are enforced before allow.
9. Conditions fail closed when missing or malformed.
10. Authorization evidence contains hashes/identifiers, not secrets.

## Architecture boundary

Capability authorization is an admission/governance decision. It does not execute tools, select providers, create credentials, or mutate runtime state. Runtime execution remains downstream of the authoritative Control API. Phase 49 definitions remain declarative; Phase 50 is the explicit layer that turns a declaration into a permitted action.

## Evidence

`tests/test_phase50_capability_authorization.py` covers explicit grants, scope escalation, deny precedence, conditions, agent declaration boundaries, subject binding, risk approval, egress policy, cost limits, and duplicate configuration rejection.

Phase 50 CI run 962 (`34625560602`) passed distribution, wheel installation/import, repository audit, integration verification, Ruff, and the complete pytest suite. The implementation was merged to `main` as `03029d301f77ff6931bfa68415893686a849201b`.

After merge, the current/index documentation was synchronized to the Phase 50-complete baseline; final exact-tree CI is the acceptance gate for that synchronized tree.

## Acceptance

All Phase 50 acceptance requirements are satisfied: implementation, tests, security/adversarial coverage, documentation, packaging verification, and CI evidence are complete pending the final exact-tree documentation synchronization gate.