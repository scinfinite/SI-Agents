# Phase 47 — OpenCode Bridge

**Status:** Implementation active; final CI gate pending.
**Roadmap:** V4 Phase 47

## Objective

Provide a first-class OpenCode protocol adapter while preserving the SI control/runtime authority boundary. OpenCode supplies transport/session/execution mechanics; SI retains caller authorization, capability policy, provenance, approvals, lifecycle authority, and audit semantics.

## Current implementation

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

## Authority invariants

1. OpenCode is a downstream harness/protocol adapter, not a second SI control plane.
2. OpenCode permissions, approval decisions, provenance, identity, and policy are never treated as SI authorization.
3. SI governance metadata is not blindly forwarded to OpenCode.
4. OpenCode session IDs are transport identifiers; SI request IDs remain canonical at the SI boundary.
5. Cancellation is exposed through the existing SI adapter contract and OpenCode abort endpoint only.
6. Streaming terminality is normalized to exactly one SI terminal response.
7. Remote OpenCode access is opt-in rather than the default.

## Upstream protocol alignment

The bridge targets the current OpenCode server surface: health, session creation, session message/prompt_async, abort, and event streaming. The upstream server source currently exposes these session operations and an SSE event surface; SI keeps this integration behind its own stable adapter contract rather than coupling core runtime code to OpenCode internals.

The bridge also follows the project's established verification principles: explicit capability discovery, injectable transports, fail-closed endpoint policy, secret-safe error normalization, deterministic tests, and no hidden authority transfer.

## Verification coverage

`tests/test_phase47_opencode.py` covers endpoint policy, health/session discovery, blocking invocation, session reuse, model forwarding, cancellation, SSE filtering, streaming terminality, streaming failures, and transport-error normalization.

## CI gate

Phase 47 may only be marked complete after the exact `main` tree containing implementation, tests, docs, and status evidence passes the full CI release gate: distribution, wheel install/import, repository audit, integration verification, Ruff, compileall, and complete pytest.
