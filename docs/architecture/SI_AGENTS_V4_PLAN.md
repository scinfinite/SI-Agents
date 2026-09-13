# SI-Agents V4 Plan

## Authority

SI-Agents V4 is built around one authoritative SI Core. Web, TUI, CLI, npm, OpenCode, runtime adapters, schedulers, agents, teams, workflows, SDKs, and integrations are clients/adapters, not competing state authorities.

```text
User → OpenCode / Web / TUI / CLI / npm / SDK → SI Core / Control API
     → Capacity → Scheduler / Orchestrator → Tasks / Agents / Teams / Workflows
     → Capability Authorization → OmniRoute → Models / Providers / APIs
     → Results / Artifacts / Evidence → SI Core
     → Observability → Evaluation → Continuous Improvement
     → Cross-Runtime → Ecosystem / Marketplace → Release Gates / Canaries / Rollback → Clients
```

OmniRoute owns model/provider/API routing. SI Core owns execution, orchestration, governance, evidence, lifecycle, persistence, recovery, waiting, workspaces, observability, evaluation, and improvement governance.

## Current position

V3 is closed. V4 has completed Phases **44–69**. Phases **46, 47, 49, 50, 58, 59, and 60** were advanced-hardened. **Phase 69 — npm Distribution + Setup is implemented at 100%. Phase 70 — End-to-End Production Validation is next.**

## Closed phases

Phases 44–69 are closed under their recorded implementation, documentation, and verification evidence. Phase 69 specifically adds the npm distribution/bootstrap surface without changing SI Core authority.

### Phase 69 — npm Distribution + Setup

**Complete / 100%.** Phase 69 delivers a thin npm launcher/bootstrapper, `npx si-agents`, global-install support, explicit `si-agents setup`, cross-platform Python discovery, an `SI_AGENTS_PYTHON` override, actionable prerequisite failures, content allowlisting, npm/Python version and license checks, exact tarball verification, and launcher smoke tests. The launcher forwards runtime commands to `core.cli.dispatch` and does not become a competing execution, authorization, or provider-routing authority.

Implementation: `package.json`, `bin/si-agents.js`, `README.npm.md`, `scripts/verify-npm-package.mjs`.

Detailed contract: `docs/architecture/phases/PHASE_69_NPM_DISTRIBUTION_SETUP.md`.

### Phase 68 — Advanced CLI Platform

**Complete / 100%.** Phase 68 delivers a transport-neutral advanced `si` CLI over SI Core. It provides governed `run create/list/get`, task/execution inspection, agent/team/workflow navigation, identity-bound approvals, bounded client sessions, event/state observation and bounded run streaming, model/provider discovery delegation, attachment inspection, non-secret config/auth status, transport profiles, and bounded declarative pipelines.

### Phase 67 — Advanced TUI Control Center

**Complete / 100%.** Phase 67 delivers a dependency-free, keyboard-first terminal operator cockpit over the existing Control API with bounded selection, filtering, deterministic sorting, detail inspection, pause/live state, direct navigation, bounded JSON status export, non-interactive rendering, governed run creation, and identity-bound approval controls.

### Phase 66 — Advanced Web Control Plane

**Complete / 100%.** Phase 66 provides a secure, accessible, same-origin operational web client over the existing WebServer and Control API.

### Phase 65 — Workflow + Automation

**Complete / 100%.** Phase 65 provides a transport-neutral declarative workflow engine with versioned DAGs, branching, bounded fan-out/loops, delegation, human gates, durable waits, triggers, retries, limits, cancellation, idempotency, checkpoints, templates, restart validation, and compensation.

## Phase 70 — End-to-End Production Validation

Validate the complete OpenCode → SI → OmniRoute → provider/model → SI → OpenCode path across agents, teams, dependencies, reviews, fallback, limits, retries, cancellation, pause/resume, checkpoints, waits, approvals, restart/session/workspace recovery, security failures, context/cost limits, control surfaces, installation, upgrades, artifacts, evidence, telemetry, and evaluation. Phase 70 must include npm clean-machine/install/upgrade validation.

## Phase 71 — Final Production Hardening

Final architecture, authority, state-machine, lifecycle, concurrency, idempotency, persistence, crash/restart, security, egress, tool/provider/runtime/context/scheduler/workspace/observability/UX/SDK/package/E2E audit with adversarial validation, performance/reliability, installation/upgrade, exact-tree, documentation, and final release evidence.

## Closure gate

A phase is closed only after implementation, unit/integration tests, adversarial/security tests, edge/failure tests, documentation synchronization, repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, SDK verification, merge, and final exact-tree mainline CI are green. Phase 69 additionally requires npm package-content, version/license, and launcher smoke verification.
