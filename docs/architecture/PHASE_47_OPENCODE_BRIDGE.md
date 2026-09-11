# Phase 47 — OpenCode Bridge

**Status:** Complete and CI-verified
**Roadmap:** V4 Phase 47

## Objective

Provide a first-class OpenCode protocol adapter while preserving the SI control/runtime authority boundary. OpenCode supplies transport/session/execution mechanics; SI retains caller authorization, capability policy, provenance, approvals, lifecycle authority, and audit semantics.

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

## Authority invariants

1. OpenCode is a downstream harness/protocol adapter, not a second SI control plane.
2. OpenCode permissions, approval decisions, provenance, identity, and policy are never treated as SI authorization.
3. SI governance metadata is not blindly forwarded to OpenCode.
4. OpenCode session IDs are transport identifiers; SI request IDs remain canonical at the SI boundary.
5. Cancellation is exposed through the existing SI adapter contract and OpenCode abort endpoint only.
6. Streaming terminality is normalized to exactly one SI terminal response.
7. Remote OpenCode access is opt-in rather than the default.
8. Events without the active OpenCode session identity are ignored by the bridge.

## Upstream protocol alignment

The bridge targets the current OpenCode server surface: health, session creation, session message/prompt_async, abort, and event streaming. The integration is intentionally isolated behind SI's stable adapter contract so upstream protocol changes do not become SI core authority changes.

## Verification coverage

`tests/test_phase47_opencode.py` covers endpoint policy, health/session discovery, blocking invocation, session reuse, model forwarding, cancellation, SSE filtering, streaming terminality, streaming failures, and transport-error normalization.

## Final verification evidence

The implementation initially ran as CI **#940 (`34615549738`)** on commit `21479716adffba5f1ab03742e2b49905666abf3b`. That gate caught two correctness gaps: cancellation was asserted after a completed request, and transport errors during session creation were not normalized. Both were corrected in commit **`52176a1d612637cbc892b354771f80e6af86910e`**.

Final Phase 47 CI **#941 (`34615709124`)** on commit `52176a1d612637cbc892b354771f80e6af86910e` completed successfully. The final job passed distribution build, wheel installation/import smoke tests, repository audit, integration verification, Ruff, compileall, and the complete pytest suite.

## Phase 47 gate result

Phase 47 is closed. The OpenCode bridge is implemented on `main`, exported through the runtime package, tested for transport/session/invocation/stream/cancellation/security-boundary behavior, documented, packaging-verified, and final-CI verified.

Phase 48 — OmniRoute Integration is the next implementation phase.
