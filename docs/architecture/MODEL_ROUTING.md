# Model Routing Contract

## Purpose

SI-Agents consumes downstream model/provider routing through a stable adapter boundary. OmniRoute may discover providers, models, health and routing capabilities, but it is never an SI authority boundary.

## Authority

```text
Control API → authorization/admission/policy/provenance/approvals
       ↓
Runtime → execution mechanics and normalized outcomes
       ↓
OmniRoute → downstream model/provider selection and inference transport
       ↓
Provider/model
```

A model or provider response cannot grant permissions, change caller identity, alter provenance, or bypass SI policy.

## Phase 48 contract

`OmniRouteBridge` implements the runtime `HarnessAdapter` contract and exposes:

- health discovery;
- `/v1/models` catalog discovery;
- typed model/provider/capability metadata;
- bounded preferred/fallback model selection;
- OpenAI-compatible `/v1/chat/completions` invocation;
- token usage normalization;
- retryability classification for rate limits and upstream failures;
- credential references resolved at transport time;
- loopback-default endpoint security;
- deterministic injectable transport for tests.

## Selection rules

Selection policy is a preference constraint, not an authorization grant. Required capabilities and cost ceilings filter the discovered catalog. Preferred and fallback model IDs are considered only if they satisfy those constraints. If no candidate satisfies the policy, the adapter returns a typed failure instead of silently selecting an incompatible model.

## Credential rules

Runtime state stores only a `OmniRouteCredentialRef` (name and environment-variable reference). Secret values are resolved when a request is sent and are never copied into events, model metadata, request metadata, errors, or persisted execution records.

## Error rules

- 429 and overload/server failures are retryable.
- transport failures normalize to timeout/transport failure without exposing upstream bodies.
- invalid or incompatible model policy is non-retryable.
- provider-specific authority or policy decisions are not imported into SI governance.

## Compatibility

The adapter targets the stable OpenAI-compatible surface used by current OmniRoute variants. Provider-specific features may be added behind explicit capability checks in later phases; SI must not reproduce OmniRoute's internal routing algorithm.

## Verification

Phase 48 tests cover endpoint policy, health/catalog discovery, capability-aware selection, cost constraints, inference, usage, metadata isolation, credential handling, error classification, no-match behavior and cancellation semantics. Final CI is the authoritative gate for release status.
