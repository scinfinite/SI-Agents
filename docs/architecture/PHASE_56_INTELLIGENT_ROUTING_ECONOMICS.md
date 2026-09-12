# Phase 56 — Intelligent Routing + Economics

## Status

**Complete on `main` after final synchronized-tree mainline CI verification.**

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

## Verification evidence

- Phase 55 prerequisite was verified closed on `main`: commit `d9c2028c302e6dafd8ebd539bdd627d893efeaa0`, synchronized-tree CI #1080 / `34678317246`.
- Phase 56 implementation PR #67 merged to `main` as merge commit `0c19e1c322b4262128b34a2203c54a30ece31f93`.
- PR CI #1091 / `34682603137` passed distribution build, wheel installation/import, repository audit, integration verification, Ruff, compileall, and full pytest.
- The initial PR CI failures were audited against pytest diagnostics and corrected before the green run.
- Final synchronized-tree mainline CI #1093 / `34682687023` passed all repository gates on commit `710d80357f81f805d3978c6af5986599f1840cb0`: distribution build, wheel installation/import, repository audit, integration verification, Ruff, compileall, and full pytest.

## Closure

Phase 56 is fully closed. The phase index is synchronized with the final evidence, and **Phase 57 — Security Platform** is the next roadmap phase.
