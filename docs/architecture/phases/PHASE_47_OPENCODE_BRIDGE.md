# Phase 47 — OpenCode Bridge

**Status:** Advanced-hardening complete; final verification pending documentation-tree CI
**Roadmap:** V4 Phase 47

## Advanced-level audit result

The original Phase 47 bridge was already a strong protocol adapter, but the audit identified missing per-request timeout propagation and an unbounded SSE frame risk. Both are now enforced at the transport boundary. OpenCode remains strictly downstream of SI authority.

## Implemented

- `core/runtime/opencode.py` provides `OpenCodeBridge` and a stdlib HTTP/SSE transport.
- OpenCode health discovery via `/global/health`.
- Session creation via `/session`, with SI `project_id` mapped only to the OpenCode directory query.
- Blocking invocation through `/session/{id}/message`.
- Streaming invocation through `/session/{id}/prompt_async` plus `/event` SSE.
- Cancellation through `/session/{id}/abort`.
- Stable SI request identity and session mapping for cancellation.
- Translation of OpenCode text parts/deltas into SI `RuntimeEvent` records.
- Translation of OpenCode terminal/error states into `InvocationResponse` without importing OpenCode authority decisions.
- Model/provider metadata forwarding only through explicit non-governance fields.
- Loopback-only default endpoint policy; remote endpoints require explicit `allow_remote=True`.
- Transport error normalization with retryability classification and no upstream response-body leakage.
- Injectable transport for deterministic tests and alternate platform clients.
- Session-filtered event consumption so global/unscoped events cannot leak another session's output into an SI invocation.
- Transport failures during session creation are normalized to a stable SI failed response.
- **Per-request timeout propagation** from `InvocationRequest.timeout_seconds` to HTTP request and SSE transport operations.
- **SSE frame bound** of 1 MiB, with oversized frames rejected before unbounded buffering.
- Streaming completion requires an explicit terminal event; premature stream end is normalized as failure.

## Authority invariants

1. OpenCode is a downstream harness/protocol adapter, not a second SI control plane.
2. OpenCode permissions, approval decisions, provenance, identity, and policy are never treated as SI authorization.
3. SI governance metadata is not blindly forwarded to OpenCode.
4. OpenCode session IDs are transport identifiers; SI request IDs remain canonical at the SI boundary.
5. Cancellation is exposed through the existing SI adapter contract and OpenCode abort endpoint only.
6. Streaming terminality is normalized to exactly one SI terminal response.
7. Remote OpenCode access is opt-in rather than the default.
8. Events without the active OpenCode session identity are ignored by the bridge.
9. Request-specific timeout budgets are passed to the downstream transport rather than silently replaced by a global default.
10. Event buffering is bounded to prevent an upstream peer from exhausting bridge memory through a single SSE frame.

## Verification coverage

`tests/test_phase47_opencode.py` covers endpoint policy, health/session discovery, blocking invocation, session reuse, model forwarding, cancellation, SSE filtering, streaming terminality, streaming failures, transport-error normalization, request timeout propagation, and bounded event transport behavior.

## Baseline evidence

Original final Phase 47 CI **#941 (`34615709124`)** passed the complete repository gate.

## Advanced-hardening evidence

Combined advanced audit CI **#984 (`34671292491`)** passed distribution, wheel verification, repository audit, integration verification, Ruff, and the complete pytest suite after the timeout/SSE hardening.

## Gate result

The Phase 47 implementation is now advanced-hardened. Final status becomes immutable on `main` only after the documentation synchronization commit also passes exact-tree CI.

Phase 48 — OmniRoute Integration is already closed and is outside this targeted hardening batch.
