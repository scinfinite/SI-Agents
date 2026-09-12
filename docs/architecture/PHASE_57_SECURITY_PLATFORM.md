# Phase 57 — Security Platform

**Status:** Implementation complete on the Phase 57 branch; PR verification CI is green. Final closure still requires merge and exact-tree mainline CI.

## Authority

Phase 57 establishes one fail-closed security authority for SI Core. Authorization is evaluated before execution and never grants credentials, execution identity, or business ownership to adapters. OmniRoute, OpenCode, tools, MCP servers, models, providers, filesystem/workspace operations, commands/processes, and network egress remain subject to SI security decisions.

## Contracts

`core/security/platform.py` provides:

- authenticated tenant-bound `Identity` records
- explicit tenant-bound `PermissionGrant` subject/action/resource/scope contracts
- least-privilege exact and bounded-prefix scope matching
- versioned `SecurityPolicy` with deny-by-default behavior
- short-lived request-bound single-use HMAC capability tokens containing tenant binding
- policy-version invalidation for issued tokens
- explicit `EgressPolicy` host/scheme allowlisting with private/loopback/link-local/reserved IP rejection
- explicit `TrustBoundary` declarations; boundaries never grant permissions by themselves
- destructive, high-risk, and credential-access approval enforcement
- secret detection/redaction before audit evidence
- conservative prompt/tool injection detection
- immutable, non-secret `AuditEvent` evidence
- deterministic `AuthorizationResult` decisions: allow, deny, or approval-required

## Security invariants

1. No authenticated identity means no authorization.
2. No explicit active tenant-bound grant means deny.
3. A grant from one tenant cannot authorize an identity from another tenant.
4. A broader tenant/project scope cannot be inferred from a narrower grant.
5. Egress is deny-by-default and only explicitly allowlisted HTTPS targets are permitted by default.
6. Private and loopback network destinations remain denied unless a policy explicitly opts into private addresses.
7. Credential-bearing external egress is always denied.
8. Destructive/high-risk operations require explicit approval; without approval they return `APPROVAL_REQUIRED` rather than silently executing.
9. Prompt/tool injection patterns cannot override policy.
10. Security tokens are bounded by TTL, tenant, subject/action/resource/scope, policy version, and single-use consumption.
11. Trust boundaries describe permitted crossings but never substitute for authorization grants.
12. Audit evidence contains only non-secret fields and redacted reasons.
13. Security policy is not an authorization bypass for runtime, provider, model, tool, or interface adapters.

## Verification

`tests/test_phase57_security_platform.py` covers least privilege, tenant and identity isolation, approval decisions, egress allowlists, private-network rejection, credential/egress separation, secret scanning/redaction, prompt/tool injection, token binding and replay prevention, token TTL, expired grants, safe audit evidence, trust-boundary non-authority, and bounded scope matching.

Phase 57 PR verification CI **#1109 / `34684116453`** passed distribution build, wheel installation/import, repository audit, integration verification, Ruff, compile/test prerequisites, and full pytest. The final closure gate remains exact-tree mainline CI after merge.
