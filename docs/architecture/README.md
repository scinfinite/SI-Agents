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

**Phases 44–67 are closed. Phase 68 is next.** Phases 46, 47, 49, 50, 58, 59, and 60 are advanced-hardened.

## Phase 67 architecture

Phase 67 upgrades the dependency-free TUI into an advanced operator control center while preserving the historical 14-view contract. The surface provides bounded list selection, deterministic filtering and sorting, detail inspection, pause/live state, direct navigation, bounded JSON status export, non-interactive rendering, and governed run/identity-bound approval commands.

`core/tui/app.py` owns only ephemeral presentation state. It calls the existing `ControlApiService` for all read data and all supported mutations. It never invokes a shell, creates an independent workflow/execution authority, or bypasses SI Core governance. `core/tui/cli.py` exposes strict page-size, root, view, filter, command, approval identity, and non-interactive controls.

Safety properties include bounded page size (1–100), bounded terminal rendering, inert unknown commands, stable navigation, explicit pause state, no shell execution, `NO_COLOR` support, and governed mutation routing. Acceptance coverage is in `tests/test_phase67_tui.py` plus the Phase 41 regression suite. See `PHASE_67_ADVANCED_TUI_CONTROL_CENTER.md` for the detailed contract.

## Phase 66 architecture

Phase 66 adds a same-origin, dependency-free web control client layered over the existing WebServer and versioned Control API. It exposes operational overview/health, live activity, workflow/run inspection, topology/DAG relationships, evidence, identity-bound approvals, governed run-request controls, resources/settings, and bounded repository source/search/diff inspection. It does not create a second state or authorization authority.

## Phase 65 architecture

Phase 65 adds a transport-neutral workflow state machine for versioned declarative DAGs. It supports conditional branching, bounded fan-out/loops, delegation, human gates, durable waits, event/webhook/interval triggers, retries, runtime limits, cancellation, request-fingerprint-bound idempotency, durable JSON checkpoints, templates, restart validation, and reverse-order compensation.

## Closure evidence

- Phase 63: PR #77 merged; final exact-tree mainline CI #1198 / `34694418960` passed.
- Phase 64: PR #78 merged; implementation closure CI #1239 / `34697885027` passed.
- Phase 65: final synchronized-tree CI #1249 / `34698187600` completed successfully.
- Phase 66: PR #79 merged; final synchronized-tree mainline CI #1284 / `34701494501` completed successfully.
- Phase 67: PR #80 merged; final PR CI #1288 / `34702115990` completed successfully.

## Current position

**Phase 67 — Advanced TUI Control Center is complete at 100%. Phase 68 — Advanced CLI Platform is next.**
