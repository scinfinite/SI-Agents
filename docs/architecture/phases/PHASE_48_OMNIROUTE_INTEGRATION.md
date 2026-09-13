# Phase 48 — OmniRoute Integration

**Status: Complete + final-CI verified**
**Roadmap:** V4 Phase 48
**Merged:** `f670563c7df06c05d269fe714e63abfe518036e0`
**Final implementation CI:** run 949 (`34623762921`) — green

## Objective

Use OmniRoute as the downstream model/provider access layer without creating a competing SI router. SI retains caller identity, authorization, governance, provenance, approvals, lifecycle authority, and audit semantics. OmniRoute supplies provider/model discovery and model inference transport.

## Implemented

- `core/runtime/omniroute.py` provides `OmniRouteBridge` and a standard-library OpenAI-compatible transport.
- Health discovery through `/health`.
- Model catalog discovery through `/v1/models` with in-process catalog caching.
- Typed model metadata including provider, capabilities, context window and cost hints.
- Capability-aware selection using explicit request policy preferences and fallback models.
- OpenAI-compatible `/v1/chat/completions` invocation.
- Runtime usage normalization for prompt/completion/total tokens.
- Retryability classification for rate limits, overload, upstream 5xx failures and transient transport failures.
- Transport failures are normalized without exposing upstream response bodies or credentials.
- Credential references resolve environment-backed secrets at request time; secret values are not stored in runtime state or metadata.
- Loopback-only default endpoint policy; remote OmniRoute requires explicit `allow_remote=True`.
- Injectable transport for deterministic tests and platform-specific clients.
- Explicitly reports cancellation as unsupported rather than pretending downstream cancellation exists.

## Authority and routing invariants

1. OmniRoute is downstream routing/provider infrastructure, not an SI control plane.
2. Model selection is a bounded preference operation over the discovered catalog; it cannot grant capabilities or authority.
3. SI governance metadata is not forwarded as OmniRoute request authority.
4. Credentials are references, never execution-state values.
5. Upstream status/body details are not copied into user-visible runtime errors.
6. A missing model/capability produces a typed non-retryable failure rather than silently selecting an unauthorized substitute.
7. Remote network access is opt-in.
8. The adapter is isolated behind the existing runtime `HarnessAdapter` contract.

## Verification

The implementation CI run **949 (`34623762921`)** passed all repository gates:

- distribution build;
- wheel installation/import smoke test;
- repository audit;
- cross-cutting integration verification;
- Ruff;
- complete pytest suite.

The final test result was **524 passed**.

The CI cycle also caught and fixed two issues before this final green run: the integration documentation marker requirement and Phase 48 transport/hygiene test failures. No phase completion claim was made before the green gate.

## Upstream alignment

Current OmniRoute variants expose OpenAI-compatible model inference and model/provider discovery surfaces. SI intentionally consumes only the stable downstream interface required by this phase and does not duplicate OmniRoute's internal routing algorithms. External engineering references are pattern research only; SI governance remains authoritative.

## Phase closure

Phase 48 is now merged into `main` and final-CI verified. Current/index documentation was synchronized after the green implementation gate, and a fresh exact-tree documentation CI gate is required before the phase is considered fully closed under the project documentation lifecycle rule.
