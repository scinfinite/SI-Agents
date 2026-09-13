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

### Current post-Phase-68 hardening baseline

- Runtime persona catalog: **300 personas across 18 divisions**.
- Capacity levels: **Low / Medium / High** with Termux-specific admission controls.
- Termux High-capacity work and local compilation: **blocked**; Desktop/Codespace are preferred.
- OpenCode and OmniRoute remain explicit integration boundaries.
- Repository-neutral provenance hygiene and Apache-2.0 licensing are in place.
- Current system specification: `SIA_SPECS.md`.
- Primary agent instructions: `AGENTS.md`.
- Current status: `docs/STATUS.md`.
- Phase archive/navigation: `docs/phases/`.

## Closed phases

Phases 44–68 are closed under their recorded implementation, merge, documentation, and CI evidence.

### Phase 68 — Advanced CLI Platform

**Complete / 100%.** Phase 68 delivers a transport-neutral advanced `si` CLI over SI Core. It provides governed `run create/list/get`, task/execution inspection, agent/team/workflow navigation, identity-bound approvals, bounded client sessions, event/state observation and bounded run streaming, model/provider discovery delegation, attachment inspection, non-secret config/auth status, transport profiles, and bounded declarative pipelines. Local mode calls `ControlApiService`; remote mode uses authenticated HTTP against the Control API.

The CLI remains an adapter rather than a second authority. Run creation is governed by SI Core; model/provider routing remains delegated to OmniRoute; resume fails closed when downstream execution owns the transition; authentication secrets are environment-only; arbitrary shell execution is not available. Existing legacy catalog/run/setup commands retain their established routing contracts.

### Phase 67 — Advanced TUI Control Center

**Complete / 100%.** Phase 67 delivers a dependency-free, keyboard-first terminal operator cockpit over the existing Control API. It preserves the historical 14-view contract and adds bounded selection, filtering, deterministic sorting, detail inspection, pause/live state, direct navigation, bounded JSON status export, non-interactive rendering, governed run creation, and identity-bound approval controls.

### Phase 66 — Advanced Web Control Plane

**Complete / 100%.** Phase 66 provides a secure, accessible, same-origin operational web client over the existing WebServer and Control API. Final synchronized-tree mainline CI #1284 / `34701494501` is green.

### Phase 65 — Workflow + Automation

**Complete / 100%.** Phase 65 provides a transport-neutral declarative workflow engine with versioned DAGs, branching, bounded fan-out/loops, delegation, human gates, durable waits, triggers, retries, limits, cancellation, idempotency, checkpoints, templates, restart validation, and compensation. Final synchronized-tree CI #1249 / `34698187600` is green.

## Phase 69 — npm Distribution + Setup

npm package/global CLI, one-command installation, platform/architecture detection, bootstrap/setup, OpenCode/OmniRoute detection/configuration, SI Core validation, diagnostics, upgrade/uninstall/migration, and clean-machine validation. The intended user-facing command is `npx si-agents`; persistent installation is `npm install -g si-agents`.

## Phase 70 — End-to-End Production Validation

Validate the complete OpenCode → SI → OmniRoute → provider/model → SI → OpenCode path across agents, teams, dependencies, reviews, fallback, limits, retries, cancellation, pause/resume, checkpoints, waits, approvals, restart/session/workspace recovery, security failures, context/cost limits, control surfaces, installation, upgrades, artifacts, evidence, telemetry, and evaluation.

## Phase 71 — Final Production Hardening

Final architecture, authority, state-machine, lifecycle, concurrency, idempotency, persistence, crash/restart, security, egress, tool/provider/runtime/context/scheduler/workspace/observability/UX/SDK/package/E2E audit with adversarial validation, performance/reliability, installation/upgrade, exact-tree, documentation, and final release evidence.

## Closure gate

A phase is closed only after implementation, unit/integration tests, adversarial/security tests, edge/failure tests, documentation synchronization, repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, SDK verification, merge, and final exact-tree mainline CI are green. **Phase 68 satisfies this gate.**
