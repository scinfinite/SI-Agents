# Phase 24 — OmniRoute Integration

## Objective

Connect SI-Agents to OmniRoute as the external model/provider gateway without duplicating OmniRoute's provider credentials, routing policy, fallback chain, quota accounting, or circuit-breaker authority.

## Delivered

- `core/provider_intelligence/omniroute.py` provides a stdlib-only OpenAI-compatible OmniRoute client.
- `OmniRouteConfig` validates absolute HTTP(S) endpoints, defaults to loopback `127.0.0.1:20128`, requires HTTPS for non-loopback remote endpoints by default, and resolves credentials only from memory or an environment variable.
- `OmniRouteClient` supports the public `/v1/models` catalog and non-streaming `/v1/chat/completions` contract.
- Model discovery is normalized into deterministic `OmniRouteModel` records.
- Health checks fail closed and never report a gateway healthy when the model endpoint cannot be reached or parsed.
- HTTP 408/409/425/429 and 5xx failures are classified as retryable; authentication and malformed-protocol failures are not silently retried.
- Session affinity, idempotency, and request correlation can be forwarded through OmniRoute's documented headers without persisting those identifiers.
- `core/provider_intelligence/omniroute_router.py` provides a thin governed invocation layer that explicitly delegates provider/model routing to OmniRoute.
- SI-side cost and latency constraints are rejected when they cannot be independently verified rather than being silently ignored.
- An SI model allowlist is accepted only for explicit model selection; `auto` is rejected with an allowlist because SI cannot prove which model OmniRoute will choose.
- No provider credentials, model keys, or OmniRoute configuration are written to the repository or user config by this phase.

## Architecture boundary

```text
OpenCode / future harnesses
        |
        v
   SI-Agents runtime
        |
        v
 OmniRouteGateway
        |
        v
 OmniRoute /v1
        |
        v
 provider accounts / local models / fallback chains
```

SI-Agents owns the invocation contract and its own governance. OmniRoute remains authoritative for provider selection, upstream credentials, provider fallback, gateway-side quotas, routing policies, and provider circuit state.

The existing `core/provider_intelligence.ModelRouter` remains useful for cases where SI owns a verified local provider catalog. Phase 24 does not route around OmniRoute or maintain a second shadow provider-fallback implementation.

## Security and cost boundaries

- API keys are accepted in memory or through `OMNIROUTE_API_KEY`; no credential persistence is performed.
- Local HTTP is allowed only for loopback addresses by default.
- Remote HTTP is rejected unless an operator explicitly disables the HTTPS requirement in process configuration.
- Error messages are bounded before being surfaced, and raw provider secrets are never intentionally included in generated errors.
- OmniRoute's own quota, pricing, caching, fallback, and provider policy remain authoritative; SI-Agents does not infer or fabricate those values.
- Future persistent configuration/installation belongs to the environment/setup phases and must preserve the same secret-handling boundary.

## Verification coverage

`tests/test_omniroute.py` covers:

- remote HTTP rejection and loopback HTTP acceptance;
- environment-based key resolution;
- deterministic model catalog normalization;
- OpenAI-compatible request construction;
- session/idempotency/request headers;
- healthy and unavailable gateway states;
- retryable HTTP 429 classification;
- successful `auto` invocation through the gateway;
- fail-closed cost constraints;
- fail-closed model allowlist handling.

CI must verify distribution build, isolated wheel installation/import, Ruff, and the full pytest suite before Phase 24 is declared complete.

## Explicit non-goals

Phase 24 does not implement:

- Termux or Codespace installers;
- `si` CLI or automatic environment setup;
- persistent OmniRoute credentials;
- OmniRoute dashboard administration or provider account management;
- a second SI-owned provider fallback/circuit system around OmniRoute;
- OpenCode configuration mutation;
- streaming normalization;
- cross-environment handoff;
- self-modifying routing policy;
- automatic paid-provider activation.

Those concerns remain governed by later phases or by the external OmniRoute deployment itself.
