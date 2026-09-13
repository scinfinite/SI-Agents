# SI-Agents V4 Plan

## Authority

SI-Agents V4 is built around one authoritative SI Core. Web, TUI, CLI, OpenCode, runtime adapters, schedulers, agents, teams, workflows, SDKs, and integrations are clients/adapters, not competing state authorities.

```text
User → OpenCode / Web / TUI / CLI / SDK → SI Core / Control API
     → Capacity → Scheduler / Orchestrator → Tasks / Agents / Teams / Workflows
     → Capability Authorization → OmniRoute → Models / Providers / APIs
     → Results / Artifacts / Evidence → SI Core
     → Observability → Evaluation → Continuous Improvement
     → Cross-Runtime → Ecosystem / Marketplace → Release Gates / Canaries / Rollback → Clients
```

OmniRoute owns model/provider/API routing. SI Core owns execution, orchestration, governance, evidence, lifecycle, persistence, recovery, waiting, workspaces, observability, evaluation, and improvement governance.

## Current position

V3 is closed. V4 has completed Phases **44–68**. Phases **46, 47, 49, 50, 58, 59, and 60** were advanced-hardened. **Phase 68 — Advanced CLI Platform is closed at 100%. Phase 69 — npm Distribution + Setup is next, after the pre-Phase 69 hardening gate.**

## Pre-Phase 69 hardening gate

Before Phase 69 implementation begins, the repository must pass the following current-state checks:

- all current documents and architecture indexes are synchronized;
- Phase records 1–68 are organized under `docs/architecture/phases/`;
- the current persona corpus contains exactly 300 definitions;
- the runtime catalog merges and validates the 21 repository-owned persona extensions;
- provenance/license/branding checks are green;
- Termux Low supports 1–2 selectable workers and Medium supports 3–5;
- High/heavy workloads are blocked on Termux and redirected to Desktop/Codespace;
- scheduler/team concurrency is clamped by capacity policy;
- OpenCode and OmniRoute remain intentional integration boundaries;
- package, wheel, CLI, SDK, Web, TUI, and repository audit checks are green;
- final exact-tree CI is green.

## Closed phases

Phases 44–68 are closed under their recorded implementation, merge, documentation, and CI evidence.

### Phase 68 — Advanced CLI Platform

**Complete / 100%.** Phase 68 delivers a transport-neutral advanced `si` CLI over SI Core. It provides governed `run create/list/get`, task/execution inspection, agent/team/workflow navigation, identity-bound approvals, bounded client sessions, event/state observation and bounded run streaming, model/provider discovery delegation, attachment inspection, non-secret config/auth status, transport profiles, and bounded declarative pipelines.

The CLI remains an adapter rather than a second authority. Run creation is governed by SI Core; model/provider routing remains delegated to OmniRoute; authentication secrets are environment-only; arbitrary shell execution is not available.

Implementation: `core/cli/platform.py`, `core/cli/aliases.py`, `core/cli/session.py`, `core/cli/profile.py`, `core/cli/dispatch.py`.

Detailed contract: `docs/architecture/phases/PHASE_68_ADVANCED_CLI_PLATFORM.md`.

### Phase 67 — Advanced TUI Control Center

**Complete / 100%.** Phase 67 delivers a dependency-free, keyboard-first terminal operator cockpit over the existing Control API with bounded selection, filtering, deterministic sorting, detail inspection, pause/live state, direct navigation, bounded JSON status export, non-interactive rendering, governed run creation, and identity-bound approval controls.

### Phase 66 — Advanced Web Control Plane

**Complete / 100%.** Phase 66 provides a secure, accessible, same-origin operational web client over the existing WebServer and Control API.

### Phase 65 — Workflow + Automation

**Complete / 100%.** Phase 65 provides a transport-neutral declarative workflow engine with versioned DAGs, branching, bounded fan-out/loops, delegation, human gates, durable waits, triggers, retries, limits, cancellation, idempotency, checkpoints, templates, restart validation, and compensation.

## Phase 69 — npm Distribution + Setup

npm package/global CLI, one-command installation, platform/architecture detection, bootstrap/setup, OpenCode/OmniRoute detection/configuration, SI Core validation, diagnostics, upgrade/uninstall/migration, and clean-machine validation.

## Phase 70 — End-to-End Production Validation

Validate the complete OpenCode → SI → OmniRoute → provider/model → SI → OpenCode path across agents, teams, dependencies, reviews, fallback, limits, retries, cancellation, pause/resume, checkpoints, waits, approvals, restart/session/workspace recovery, security failures, context/cost limits, control surfaces, installation, upgrades, artifacts, evidence, telemetry, and evaluation.

## Phase 71 — Final Production Hardening

Final architecture, authority, state-machine, lifecycle, concurrency, idempotency, persistence, crash/restart, security, egress, tool/provider/runtime/context/scheduler/workspace/observability/UX/SDK/package/E2E audit with adversarial validation, performance/reliability, installation/upgrade, exact-tree, documentation, and final release evidence.

## Closure gate

A phase is closed only after implementation, unit/integration tests, adversarial/security tests, edge/failure tests, documentation synchronization, repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, SDK verification, merge, and final exact-tree mainline CI are green. **Phase 68 satisfies its original closure gate; the current hardening gate is required before Phase 69 begins.**
