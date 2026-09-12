# Phase 56 — Intelligent Routing + Economics

## Status

**In implementation.** The implementation is on `phase-56-intelligent-routing`; final synchronized-tree mainline CI is required before closure.

## Authority boundary

SI Core owns task orchestration, authorization, lifecycle, budgets, evidence, and execution state. OmniRoute remains the external model/provider/API routing authority. Phase 56 adds SI-side routing intelligence without duplicating provider credentials or granting capabilities.

## Delivered contracts

- `TaskRequirements` expresses capabilities, context, token, cost, latency, streaming, structured-output, vision, preference, reliability, and escalation/downgrade constraints.
- `infer_complexity` deterministically classifies a task as simple, moderate, complex, or critical from explicit request signals.
- `ModelProfile` now records quality and supports streaming/structured-output capabilities in addition to chat/code/reasoning/vision/tool-use/embeddings.
- `IntelligentRouter` ranks eligible candidates using quality, reliability history, latency, cost, provider/model preference, quota, and circuit state.
- Context and output limits are enforced before a route is selected.
- `BudgetLedger` provides reservation and settlement guards; durable budget ownership remains in SI Core.
- `RouteEvidence` records non-secret decision evidence including complexity, selected candidate, candidate count, escalation level, attempt, failure classification, and retry-cost forecast.
- Bounded fallback supports transient/rate-limit recovery with explicit escalation/downgrade controls.
- Health observations and circuit breakers prevent repeatedly failing providers from remaining eligible.
- Retry economics are deterministic and bounded by `RoutePolicy.max_attempts` and `retry_multiplier`.

## Security and failure invariants

- No routing path grants a capability or execution authority.
- Disabled models/providers, excluded providers, exhausted quotas, open circuits, insufficient context/output capacity, and minimum-reliability violations are fail-closed.
- Budget reservations cannot exceed remaining budget; negative costs are rejected.
- Fallback cannot exceed the configured attempt budget.
- Route evidence contains no credentials or secret-like provider material.
- Stable tie-breaking makes decisions reproducible for equal scores.
- Unknown health is neutral; observed degradation lowers eligibility quality rather than silently changing authorization.

## Verification plan

The Phase 56 test suite covers complexity inference, capability/context matching, vision/streaming/structured-output constraints, economic scoring, preferences, quota exhaustion, health degradation, circuit opening, budget reservation, retry economics, bounded fallback, escalation/downgrade, forecasting, and stale quota observations.

Closure requires the repository's standard gates: distribution build and wheel verification, repository audit, integration verification, Ruff, compileall, full pytest, documentation/index synchronization, and final exact-tree mainline CI.

## Phase 55 prerequisite

Phase 55 was verified fully closed before this phase began. `main` points to `d9c2028c302e6dafd8ebd539bdd627d893efeaa0`, and synchronized-tree CI #1080 / run `34678317246` completed successfully. The Phase 55 record and index now identify that run as the final closure gate.
