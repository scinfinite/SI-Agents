# SI-Agents V4 Plan

## Authority

SI-Agents V4 is built around one authoritative SI Core. Web, TUI, CLI, OpenCode, runtime adapters, schedulers, agents, teams, workflows, SDKs, and integrations are clients/adapters, not competing state authorities.

```text
User → OpenCode / Web / TUI / CLI / SDK → SI Core / Control API
     → Scheduler / Orchestrator → Tasks / Agents / Teams / Workflows
     → Capability Authorization → OmniRoute → Models / Providers / APIs
     → Results / Artifacts / Evidence → SI Core
     → Observability → Evaluation → Continuous Improvement
     → Cross-Runtime → Ecosystem / Marketplace → Release Gates / Canaries / Rollback → Clients
```

OmniRoute owns model/provider/API routing. SI Core owns execution, orchestration, governance, evidence, lifecycle, persistence, recovery, waiting, workspaces, observability, evaluation, and improvement governance.

## Current position

V3 is closed. V4 has completed Phases **44–68**. Phases **46, 47, 49, 50, 58, 59, and 60** were advanced-hardened. **Phase 68 — Advanced CLI Platform is closed at 100%. Phase 69 — npm Distribution + Setup is next.**

## Closed phases

Phases 44–68 are closed under their recorded implementation, merge, documentation, and CI evidence.

### Phase 68 — Advanced CLI Platform

**Complete / 100%.** Phase 68 delivers a transport-neutral advanced `si` CLI over SI Core. It provides governed `run create/list/get`, task/execution inspection, agent/team/workflow navigation, identity-bound approvals, bounded client sessions, event/state observation and bounded run streaming, model/provider discovery delegation, attachment inspection, non-secret config/auth status, transport profiles, and bounded declarative pipelines. Local mode calls `ControlApiService`; remote mode uses authenticated HTTP against the Control API.

The CLI remains an adapter rather than a second authority. Run creation is governed by SI Core; model/provider routing remains delegated to OmniRoute; resume fails closed when downstream execution owns the transition; authentication secrets are environment-only; arbitrary shell execution is not available. Existing legacy catalog/run/setup commands retain their established routing contracts.

Machine operation is a first-class contract: deterministic JSON envelopes, stable exit classes, 1 MiB remote request/response bounds, 10 MiB attachment inspection, 256 KiB pipeline files, 100 pipeline steps, 100 sessions, 32 non-secret profiles, bounded streaming, path-safe identifiers, and fail-closed authority boundaries.

Implementation: `core/cli/platform.py`, `core/cli/aliases.py`, `core/cli/session.py`, `core/cli/profile.py`, `core/cli/dispatch.py`.

Acceptance coverage: `tests/test_phase68_cli.py` plus the complete repository suite. Detailed contract: `docs/architecture/PHASE_68_ADVANCED_CLI_PLATFORM.md`.

PR #81 merged successfully as commit `8c5fb08e9c8a5628f59cf929e3c2ac203d4eac29`. Final PR CI **#1319** / run **34703142494**, SDK CI **#111** / run **34703142515**, and merged-tree mainline CI **#1320** / run **34703212232** completed successfully.

### Phase 67 — Advanced TUI Control Center

**Complete / 100%.** Phase 67 delivers a dependency-free, keyboard-first terminal operator cockpit over the existing Control API. It preserves the historical 14-view contract and adds bounded selection, filtering, deterministic sorting, detail inspection, pause/live state, direct navigation, bounded JSON status export, non-interactive rendering, governed run creation, and identity-bound approval controls.

PR #80 merged successfully. Final PR CI **#1288** / run **34702115990** completed successfully.

### Phase 66 — Advanced Web Control Plane

**Complete / 100%.** Phase 66 provides a secure, accessible, same-origin operational web client over the existing WebServer and Control API. Final synchronized-tree mainline CI #1284 / `34701494501` is green.

### Phase 65 — Workflow + Automation

**Complete / 100%.** Phase 65 provides a transport-neutral declarative workflow engine with versioned DAGs, branching, bounded fan-out/loops, delegation, human gates, durable waits, triggers, retries, limits, cancellation, idempotency, checkpoints, templates, restart validation, and compensation. Final synchronized-tree CI #1249 / `34698187600` is green.

## Phase 69 — npm Distribution + Setup

npm package/global CLI, one-command installation, platform/architecture detection, bootstrap/setup, OpenCode/OmniRoute detection/configuration, SI Core validation, diagnostics, upgrade/uninstall/migration, and clean-machine validation.

## Phase 70 — End-to-End Production Validation

Validate the complete OpenCode → SI → OmniRoute → provider/model → SI → OpenCode path across agents, teams, dependencies, reviews, fallback, limits, retries, cancellation, pause/resume, checkpoints, waits, approvals, restart/session/workspace recovery, security failures, context/cost limits, control surfaces, installation, upgrades, artifacts, evidence, telemetry, and evaluation.

## Phase 71 — Final Production Hardening

Final architecture, authority, state-machine, lifecycle, concurrency, idempotency, persistence, crash/restart, security, egress, tool/provider/runtime/context/scheduler/workspace/observability/UX/SDK/package/E2E audit with adversarial validation, performance/reliability, installation/upgrade, exact-tree, documentation, and final release evidence.

## Closure gate

A phase is closed only after implementation, unit/integration tests, adversarial/security tests, edge/failure tests, documentation synchronization, repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, SDK verification, merge, and final exact-tree mainline CI are green. **Phase 68 satisfies this gate.**