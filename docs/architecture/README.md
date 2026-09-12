# Architecture

SI-Agents V4 uses a single authoritative SI Core. Web, TUI, CLI, OpenCode, SDKs, runtime adapters, schedulers, agents, teams, workflows, and integrations are clients/adapters of that authority rather than independent state owners.

## V4 target architecture

```text
OpenCode / Web / TUI / CLI / SDK → SI Core / Control API
                                 → Scheduler / Orchestrator
                                 → Tasks / Agents / Teams / Workflows
                                 → Capability Authorization → OmniRoute
                                 → Models / Providers / APIs
                                 → Results / Artifacts / Evidence
                                 → Observability → Evaluation → Continuous Improvement
                                 → Cross-Runtime Gateway → Ecosystem / Marketplace → Clients / Harnesses
```

OmniRoute owns model/provider/API routing. SI Core owns execution, orchestration, governance, evidence, lifecycle, persistence, recovery, waiting, workspaces, observability, evaluation, continuous improvement, and cross-runtime governance.

## Verified V4 phases

**Phases 44–65 are closed.** Phases 46, 47, 49, 50, 58, 59, and 60 are advanced-hardened. **Phase 66 — Advanced Web Control Plane is next.**

## Phase 65 architecture

Phase 65 adds a transport-neutral workflow state machine for versioned declarative DAGs. It supports conditional branching, bounded fan-out/loops, delegation, human gates, durable waits, event/webhook/interval triggers, retries, runtime limits, cancellation, request-fingerprint-bound idempotency, durable JSON checkpoints, templates, restart validation, and reverse-order compensation.

Workflow definitions and persisted runs contain only JSON-safe data. Action/condition/delegate callables are explicit process-local adapters and never become persisted authority. Loop termination predicates are evaluated after each bounded iteration, while ordinary step predicates control branch eligibility. SI Core remains the authorization and execution authority.

See `PHASE_65_WORKFLOW_AUTOMATION.md` for the detailed contract and security invariants.

## Phase 64 architecture

Phase 64 adds typed Python and TypeScript SDK adapters over the versioned Control API. REST, SSE, and WebSocket transports remain observational/client surfaces; governance and execution authority stay inside SI Core. Cursor pagination is filter-bound, authentication is header-only, idempotency is bounded, and event subscriptions have explicit lifecycle.

See `PHASE_64_SDK_DEVELOPER_PLATFORM.md` for the detailed Phase 64 contract and security invariants.

## Closure evidence

- Phase 63: PR #77 merged; final exact-tree mainline CI #1198 / `34694418960` passed on `633af3e9a5b1a106fafee37c4c95d0b18e19743e`.
- Phase 64: PR #78 merged; implementation-tree closure CI #1239 / `34697885027` passed the repository closure suite.
- Phase 65: final synchronized-tree CI #1249 / `34698187600` completed successfully with distribution build, wheel verification, repository audit, integration verification, Ruff, and full pytest all green.

## Current position

**Phase 65 — Workflow + Automation is 100% complete. Phase 66 — Advanced Web Control Plane is next.**
