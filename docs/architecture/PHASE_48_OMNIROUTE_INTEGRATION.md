# Phase 48 — OmniRoute Integration

**Status:** Implementation complete; pending final CI gate
**Roadmap:** V4 Phase 48

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
- Retryability classification for rate limits, overload and upstream 5xx failures.
- Transport failures are normalized without exposing upstream response bodies or credentials.
- Credential references resolve environment-backed secrets at request time; secret values are not stored in runtime state or metadata.
- Loopback-only default endpoint policy; remote OmniRoute requires explicit `allow_remote=True`.
- Injectable transport for deterministic tests and platform-specific clients.
- Explicitly reports cancellation as unsupported rather than pretending downstream cancellation exists.

## Authority and routing invariants

1. OmniRoute is downstream routing/provider infrastructure, not an SI control plane.
2. Model selection is a bounded preference operation over the discovered catalog; it cannot grant capabilities or authority.
3. SI governance metadata is not forwarded as OmniRoute request authority.
4. Credentials are references, never SI execution-state values.
5. Upstream status/body details are not copied into user-visible runtime errors.
6. A missing model/capability produces a typed non-retryable failure rather than silently selecting an unauthorized substitute.
7. Remote network access is opt-in.
8. The adapter is isolated behind the existing runtime `HarnessAdapter` contract.

## Upstream alignment

Current OmniRoute implementations expose an OpenAI-compatible inference surface and commonly provide health/model catalog endpoints; newer variants also expose route explanation, statistics, quota-aware selection, and provider catalogs. SI intentionally consumes only the stable downstream interface required by Phase 48 and does not duplicate OmniRoute's routing algorithms.

External reference research also confirmed that modern OmniRoute variants support OpenCode compatibility and model/provider catalogs. The design therefore keeps OpenCode as the interactive harness and OmniRoute as its downstream model access layer, preserving the Phase 47 boundary.

## Verification coverage

`tests/test_phase48_omniroute.py` covers endpoint security, health/catalog discovery, capability-aware selection, cost policy, OpenAI-compatible invocation, structured messages, governance-metadata isolation, credential resolution, rate-limit/error normalization, no-match behavior, and explicit cancellation semantics.

The phase also incorporates reference patterns from current ECC/Agency Agents practice: explicit quality/evidence gates, specialist boundaries, and evidence over assertions rather than treating an external project as an implementation dependency.

## Final gate

This record must only be marked **Complete + final-CI verified** after the implementation is merged into `main`, all current/index documentation is synchronized, and the exact-tree repository CI passes distribution, wheel import, repository audit, integration verification, Ruff, compileall, and the complete pytest suite.
