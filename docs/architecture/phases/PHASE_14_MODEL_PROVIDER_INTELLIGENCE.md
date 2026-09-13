# Phase 14 — Model/Provider Intelligence

## Status

**Complete when the final main-branch CI run for the Phase 14 head is green.**

## Purpose

Phase 14 makes model/provider selection an evidence-bearing decision rather than a hard-coded preference. The intelligence layer records model capabilities, token limits, cost, latency, reliability, provider priority, free/paid status, quota observations, and provider health. A deterministic router uses those signals to select a suitable model while preserving hard constraints.

## Architecture

```text
RoutingRequest
      |
      v
ProviderRegistry -> QuotaTracker
      |                 |
      +-------> ModelRouter <------- CircuitBreaker
                    |
                    v
             RoutingDecision
```

### Model/provider registry

`ProviderRegistry` requires explicit provider registration, rejects duplicates, validates model metadata, and exposes only enabled entries. Registration is metadata and never grants execution permission.

### Capability matching

Required capabilities are hard constraints. Unknown or absent capability support is never assumed. The router therefore cannot select a model that fails the requested capability set.

### Cost and free-first routing

Estimated input/output token cost is calculated from per-million-token rates. Optional cost ceilings are hard constraints. When free-first routing is enabled, free providers receive a deterministic preference. Paid usage is still governed by Phase 13 approval policy; this router does not bypass governance.

### Quota

`QuotaTracker` stores the freshest observed quota snapshot per provider. An explicitly exhausted request/token quota removes that provider from candidates. Unknown quota remains unknown rather than being fabricated as exhausted or unlimited.

### Reliability and latency

Model reliability and observed health are represented separately from static metadata. The router scores reliability, latency, cost, free-first preference, and provider priority deterministically. Health observations are bounded to prevent unbounded in-memory growth.

### Fallback and circuit breaking

A provider circuit opens after a configurable failure threshold and temporarily removes that provider from routing. Fallback is simply re-ranking remaining eligible candidates; capability, cost, latency, quota, and exclusion constraints remain in force.

## Safety boundaries

- The router selects; it does not execute provider calls.
- No API keys, tokens, or credentials are stored in model/provider configuration.
- Unknown capabilities are not treated as supported.
- Unknown cost is not treated as free.
- Paid-resource governance remains authoritative.
- Circuit breaking is a reliability mechanism, not a security boundary.
- Provider metadata is advisory and must be refreshed by trusted adapters before being treated as current.

## Verification

The Phase 14 adversarial suite covers duplicate registration, capability mismatch, free-first selection, cost and latency ceilings, quota exhaustion and freshness, circuit opening/reset/fallback, bounded health tracking, invalid costs/models, exclusions, and bidirectional token-cost calculation. Completion requires the repository CI build, Ruff, and tests to pass on the final Phase 14 head.
