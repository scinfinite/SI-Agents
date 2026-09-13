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

V3 is closed. V4 has completed Phases **44–70**. Phases **46, 47, 49, 50, 58, 59, and 60** were advanced-hardened. **Phase 70 — End-to-End Production Validation is complete at 100%. Phase 71 — Final Production Hardening is next.**

## Closed phases

Phases 44–70 are closed under their recorded implementation, documentation, and verification evidence. Phase 70 validates the production control/data path without introducing a second execution authority.

### Phase 70 — End-to-End Production Validation

**Complete / 100%.** Phase 70 validates OpenCode → SI RuntimeEngine → OmniRoute → model/provider boundary → SI → OpenCode using deterministic CI-safe boundary transports. It adds direct end-to-end acceptance coverage plus governance-denial, session-isolation, model-fallback, and cancellation-boundary checks. Existing runtime, OpenCode, OmniRoute, Web/TUI/CLI, SDK, wheel, npm, repository-audit, compileall, Ruff, and full pytest gates remain mandatory and green.

Implementation/test coverage: `tests/integration/test_phase70_production_path.py`.

Detailed acceptance record: `docs/architecture/phases/PHASE_70_END_TO_END_PRODUCTION_VALIDATION.md`.

### Phase 69 — npm Distribution + Setup

**Complete / 100%.** Phase 69 delivers a thin npm launcher/bootstrapper, `npx si-agents`, global-install support, explicit `si-agents setup`, cross-platform Python discovery, an `SI_AGENTS_PYTHON` override, actionable prerequisite failures, content allowlisting, npm/Python version and license checks, exact tarball verification, and launcher smoke tests. The launcher forwards runtime commands to `core.cli.dispatch` and does not become a competing execution, authorization, or provider-routing authority.

Implementation: `package.json`, `bin/si-agents.js`, `README.npm.md`, `scripts/verify-npm-package.mjs`.

Detailed contract: `docs/architecture/phases/PHASE_69_NPM_DISTRIBUTION_SETUP.md`.

## Phase 71 — Final Production Hardening

Final architecture, authority, state-machine, lifecycle, concurrency, idempotency, persistence, crash/restart, security, egress, tool/provider/runtime/context/scheduler/workspace/observability/UX/SDK/package/E2E audit with adversarial validation, performance/reliability, installation/upgrade, exact-tree, documentation, and final release evidence.

## Closure gate

A phase is closed only after implementation, unit/integration tests, adversarial/security tests, edge/failure tests, documentation synchronization, repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, SDK verification, merge, and final exact-tree mainline CI are green. Phase 69 additionally requires npm package-content, version/license, and launcher smoke verification. Phase 70 additionally requires deterministic end-to-end production-path coverage and explicit failure-containment checks.
