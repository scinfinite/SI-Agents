# Phase 24 — OmniRoute Integration

**Status: Complete — implementation and CI verified.**

## Objective

Connect SI-Agents to OmniRoute as the external model/provider gateway without duplicating OmniRoute's provider credentials, routing policy, fallback chain, quota accounting, or circuit-breaker authority.

## Delivered

- `core/provider_intelligence/omniroute.py` provides a stdlib-only OpenAI-compatible OmniRoute client.
- Configuration validates absolute HTTP(S) endpoints, loopback defaults, and credential resolution only from memory/environment.
- Model discovery is normalized into deterministic records.
- Health checks fail closed.
- Retryable transport failures are classified conservatively.
- Session affinity, idempotency, and request correlation can be forwarded without persistence.
- `omniroute_router.py` provides a thin governed invocation layer that explicitly delegates provider/model routing to OmniRoute.
- SI-side constraints fail closed when they cannot be independently verified.
- No provider credentials or model keys are persisted by this phase.

## Architecture boundary

```text
OpenCode / future harnesses
        |
   SI-Agents runtime
        |
   OmniRoute gateway
        |
 OmniRoute /v1
        |
 provider accounts / local models / fallback chains
```

SI-Agents owns its invocation contract and governance. OmniRoute remains authoritative for provider selection, upstream credentials, provider fallback, gateway-side quotas, routing policies, and provider circuit state.

## Security and cost boundaries

API keys are accepted only through the established in-memory/environment boundary. Local HTTP is restricted to loopback by default; remote endpoints require HTTPS by default. Error handling is bounded. SI-Agents does not infer or fabricate provider pricing, quota, fallback, or circuit state.

## Verification coverage

Tests cover endpoint validation, credential resolution, deterministic model normalization, request construction, correlation headers, health/failure states, retry classification, successful invocation, and fail-closed model/cost constraints. The completed phase was verified through repository distribution, Ruff, and full pytest CI gates.

## Current-state addendum

Phases 25–29 built environment readiness, CLI/setup, handoff, and personas around the OmniRoute boundary. OmniRoute remains the authoritative model/provider routing layer. Phase 30 must not introduce a competing provider router. Current repository status is Phase 29 complete; Phase 30 is next.
