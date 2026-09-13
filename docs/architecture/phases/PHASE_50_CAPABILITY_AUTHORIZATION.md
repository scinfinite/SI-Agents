# Phase 50 — Capability Authorization

## Status

**Advanced-hardening complete; final verification pending documentation-tree CI.**

## Objective

Convert agent/team capability declarations into explicit, fail-closed, auditable authorization decisions without allowing an agent, team, model, provider, or runtime adapter to self-grant authority.

## Advanced-level audit result

The original Phase 50 evaluator already enforced explicit grants, scope, deny precedence, declared capabilities, risk approvals, cost controls, and fail-closed egress. The hardening audit found that high-risk approvals were reusable unless bound to the exact authorization request, and governance metadata accepted secret-like keys. Both gaps are now closed.

## Delivered

- `AuthorizationRequest` with caller subject, requested capabilities, resource scope, risk, metadata, estimated cost, egress flag, approval and provenance.
- Deterministic SHA-256 request fingerprint over the authorization decision inputs, excluding approval itself.
- `CapabilityAuthorizer` with exact/descendant scope matching, explicit grants, explicit deny precedence, condition matching, declared-capability enforcement, risk approval gates, cost-policy enforcement, and fail-closed egress policy.
- **Request-bound high/critical approvals:** approval references must equal the exact request fingerprint, preventing approval replay against changed scope/capabilities/cost/metadata.
- **Secret-like metadata rejection:** keys resembling passwords, secrets, tokens, API keys, private keys, or credentials are rejected before authorization evidence can be produced.
- Bounded subject/scope/capability/metadata/provenance lengths to reduce abuse and evidence amplification.
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
6. High/critical-risk requests require active approval bound to the exact request fingerprint.
7. External egress requires an explicit allow policy; absence of policy is deny.
8. Cost limits are enforced before allow.
9. Conditions fail closed when missing or malformed.
10. Authorization evidence contains hashes/identifiers, not secrets.
11. Secret-like governance metadata keys are rejected before authorization.
12. Approval material cannot be replayed after changing any fingerprinted authorization input.

## Architecture boundary

Capability authorization is an admission/governance decision. It does not execute tools, select providers, create credentials, or mutate runtime state. Runtime execution remains downstream of the authoritative Control API. Phase 49 definitions remain declarative; Phase 50 is the explicit layer that turns a declaration into a permitted action.

## Verification coverage

`tests/test_phase50_capability_authorization.py` covers explicit grants, scope escalation, deny precedence, conditions, agent declaration boundaries, subject binding, active/expired/bound/unbound approvals, approval replay prevention, egress policy semantics, cost limits, secret-like metadata rejection, and duplicate configuration rejection.

## Baseline evidence

Phase 50 CI run 962 (`34625560602`) passed distribution, wheel installation/import, repository audit, integration verification, Ruff, and the complete pytest suite. The implementation was merged to `main` as `03029d301f77ff6931bfa68415893686a849201b`.

## Advanced-hardening evidence

Combined advanced audit CI **#984 (`34671292491`)** passed distribution, wheel verification, repository audit, integration verification, Ruff, and the complete pytest suite after the approval-binding and metadata-secrecy hardening.

## Acceptance

The Phase 50 authorization layer is now advanced-hardened. Final status becomes immutable on `main` only after the documentation synchronization commit also passes exact-tree CI.
