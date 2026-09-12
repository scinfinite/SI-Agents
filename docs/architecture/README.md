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

**Phases 44–68 are closed.** Phases 46, 47, 49, 50, 58, 59, and 60 are advanced-hardened.

## Production Web Control Center

The approved Web Control Center visual system is implemented on `main`. It is the reference visual language for SI-Agents browser operations: compact operator typography, dark navy/light neutral surfaces, restrained semantic accents, responsive navigation, dense but readable cards/tables, status badges, and accessible controls.

The web supports **dark and light modes**, with local theme persistence and operating-system preference fallback. The production navigation preserves the full Control Center read surface: Overview, Runs, Agents, Teams, Workflows, Topology, Skills, Memory, Knowledge, Evidence, Organization, Governance, Environments, Harnesses, and Settings.

Overview hydrates live snapshot/health/runs/events data; collection screens support filtering; global search can query supported resource surfaces; refresh rehydrates the current view; and Topology provides organization/workflow/capability graph modes with node filtering, keyboard inspection, pan, zoom, and reset. Mobile navigation, visible keyboard focus, reduced-motion behavior, and semantic labels are included.

The browser remains an adapter of the existing versioned Control API. It does not execute agents, workflows, shell commands, tools, or providers directly. Detailed design contract: `WEB_CONTROL_CENTER_DESIGN.md`.

## Phase 68 architecture

Phase 68 adds an advanced CLI adapter over the existing Control API. Local CLI calls use `ControlApiService`; remote CLI calls use authenticated HTTP. The platform exposes governed runs/tasks/executions, agent/team/workflow resources, identity-bound approvals, bounded client sessions, events and bounded run streaming, model/provider delegation, attachment inspection, non-secret configuration/auth status, transport profiles, and bounded declarative pipelines.

The CLI owns no execution state authority. Run creation is always submitted through SI Core governance. Resume explicitly fails closed when downstream execution owns the transition. Model/provider discovery remains delegated to OmniRoute. Client metadata is bounded and stored separately from SI Core lifecycle state. Authentication tokens are environment-only and never printed or persisted by the CLI. Established legacy commands retain their historical routing contracts.

Machine operation is a first-class contract: JSON envelopes are deterministic, exit classes distinguish success/operational/auth/governance failure, remote payloads are bounded, identifiers are path-safe, and streaming/pipeline/attachment/session/profile surfaces have explicit resource limits. No command performs arbitrary shell execution.

Implementation: `core/cli/platform.py`, `core/cli/aliases.py`, `core/cli/session.py`, `core/cli/profile.py`, and `core/cli/dispatch.py`. Detailed contract: `PHASE_68_ADVANCED_CLI_PLATFORM.md`.

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
- Phase 67: PR #80 merged; final synchronized-tree mainline CI #1295 / `34702226193` completed successfully.
- Phase 68: PR #81 merged; final PR CI #1319 / `34703142494`, SDK CI #111 / `34703142515`, and merged-tree mainline CI #1320 / `34703212232` completed successfully.
- Web Control Center design: PR #82 merged; final synchronized-tree CI is the release gate for the design/documentation commit.

## Current position

**Phase 68 — Advanced CLI Platform is 100% complete and closed. The approved Web Control Center design is implemented. Phase 69 — npm Distribution + Setup is next.**