# Phase 57 — Security Platform

**Status:** In implementation until final synchronized-tree mainline CI passes.

## Authority

Phase 57 establishes one fail-closed security authority for SI Core. Authorization is evaluated before execution and never grants credentials, execution identity, or business ownership to adapters. OmniRoute, OpenCode, tools, MCP servers, models, providers, filesystem/workspace operations, commands/processes, and network egress remain subject to SI security decisions.

## Contracts

`core/security/platform.py` provides:

- authenticated tenant-bound `Identity` records
- explicit `PermissionGrant` subject/action/resource/scope contracts
- least-privilege exact and bounded-prefix scope matching
- versioned `SecurityPolicy` with deny-by-default behavior
- short-lived HMAC capability tokens bound to subject/action/resource/scope/policy version
- single-use token consumption and policy-version invalidation
- explicit `EgressPolicy` host/scheme allowlisting with private/loopback/link-local/reserved IP rejection
- explicit `TrustBoundary` declarations; boundaries never grant permissions by themselves
- destructive, high-risk, and credential-access approval enforcement
- secret detection/redaction before audit evidence
- conservative prompt/tool injection detection
- immutable, non-secret `AuditEvent` evidence
- deterministic `AuthorizationResult` decisions: allow, deny, or approval-required

## Security invariants

1. No authenticated identity means no authorization.
2. No explicit active grant means deny.
3. A broader tenant/project scope cannot be inferred from a narrower grant.
4. Egress is deny-by-default and only explicitly allowlisted HTTPS targets are permitted by default.
5. Private and loopback network destinations remain denied unless a policy explicitly opts into private addresses.
6. Credential-bearing external egress is always denied.
7. Destructive/high-risk operations require explicit approval.
8. Prompt/tool injection patterns cannot override policy.
9. Security tokens are bounded by TTL, request attributes, policy version, and single-use consumption.
10. Trust boundaries describe permitted crossings but never substitute for authorization grants.
11. Audit evidence contains only non-secret fields and redacted reasons.
12. Security policy is not an authorization bypass for runtime, provider, model, tool, or interface adapters.

## Verification

`tests/test_phase57_security_platform.py` covers least privilege, identity and tenant isolation, approvals, egress allowlists, private-network rejection, credential/egress separation, secret scanning/redaction, prompt/tool injection, token binding and replay prevention, token TTL, expired grants, safe audit evidence, trust-boundary non-authority, and bounded scope matching.

Phase closure additionally requires repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, and final exact-tree mainline CI.
