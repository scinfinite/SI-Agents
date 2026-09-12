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

Phases 44–63 are closed. Phases 46, 47, 49, 50, 58, 59, and 60 are advanced-hardened.

## Phase 64 architecture

Phase 64 adds typed Python and TypeScript SDK adapters over the versioned Control API. REST, SSE, and WebSocket transports remain observational/client surfaces; governance and execution authority stay inside SI Core. Cursor pagination is filter-bound, authentication is header-only, idempotency is bounded, and event subscriptions have explicit lifecycle.

See `PHASE_64_SDK_DEVELOPER_PLATFORM.md` for the detailed Phase 64 contract and security invariants.

## Phase 63 closure evidence

- PR #77 merged into `main` as `19be0c14774e7073871a21fde42132a73c2a77d4`.
- PR CI #1189 / `34694186010` passed wheel verification, repository audit, integration verification, Ruff, and full pytest.
- Final exact-tree mainline CI #1198 / `34694418960` passed on `633af3e9a5b1a106fafee37c4c95d0b18e19743e`.

## Current position

**Phase 64 — SDK / Developer Platform is in implementation pending final exact-tree mainline CI.**
