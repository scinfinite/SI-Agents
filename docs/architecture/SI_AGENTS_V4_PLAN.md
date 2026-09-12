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

V3 is closed. V4 has completed Phases **44–64** and is implementing **Phase 65 — Workflow + Automation**. Phases **46, 47, 49, 50, 58, 59, and 60** were advanced-hardened. Phase 64 is merged to `main`; its exact synchronized-tree closure remains subject to the repository-wide mainline CI gate.

## Closed phases

Phases 44–63 are closed under their recorded implementation/merge evidence. Phase 64 implementation is merged; the final synchronized-tree mainline CI is its closure gate.

### Phase 63 — Ecosystem / Marketplace

Phase 63 establishes governed ecosystem metadata and lifecycle contracts for future agents, skills, tools, teams, workflows, model/provider profiles, and MCP extensions. `MarketplaceManifest` provides strict semver, dependencies, compatibility declarations, permission declarations, provenance/trust, payload identity, and exact manifest identity. `MarketplaceRegistry` provides deterministic package/version lookup and templates. `EcosystemManager` provides governed install/update/uninstall/rollback, bounded lifecycle history, and drift detection.

The lifecycle layer is governance-neutral and does not execute package payloads or grant capabilities. Untrusted packages require an explicit governance hook, requested permissions must be declared, and governance approval is bound to the exact manifest digest. SI Core remains authoritative for authorization and execution.

Implementation: `core/marketplace/registry.py` and `core/marketplace/__init__.py`.

Verification: `tests/unit/test_phase63_marketplace.py`, PR #77 / CI #1189 (`34694186010`), and final exact-tree mainline CI #1198 (`34694418960`) on `633af3e9a5b1a106fafee37c4c95d0b18e19743e`.

## Phase 64 — SDK / Developer Platform

Phase 64 delivers Python and TypeScript SDKs, versioned REST/WebSocket/SSE access, typed schemas and stable errors, optional bearer authentication, header-bound identity, idempotent run creation, bounded concurrency, cursor pagination/filtering, event subscriptions, signed webhook delivery primitives, OpenAPI updates, package metadata, examples, and adversarial tests. SDKs remain clients and do not gain governance or execution authority.

Implementation: `sdk/python/si_agents`, `sdk/typescript`, `core/control_api/pagination.py`, `core/control_api/subscriptions.py`, and SDK transport extensions in `core/control_api/server.py` / `openapi.py`.

Documentation: `docs/architecture/PHASE_64_SDK_DEVELOPER_PLATFORM.md`.

PR #78 was merged into `main`. The dedicated SDK gate is green from the implementation cycle; the synchronized documentation tree must pass the complete mainline closure suite before Phase 64 can be marked fully closed.

## Phase 65 — Workflow + Automation — active

Scope: sequential/parallel-capable DAG orchestration, conditional branching, bounded loops and fan-out, delegation, human gates, durable waits/timers, event/webhook/interval triggers, retries and failure handling, compensation/rollback, checkpoints/resume, versioning/templates/import/export, and developer integrations.

Current implementation: `core/automation/workflows.py`.

Current verification: `tests/unit/test_phase65_workflows.py` covers DAG branching, durable waits, human gates, fan-out/loops, event/webhook/interval triggers, retries, runtime expiry, concurrent idempotency, cancellation, persistence corruption, templates/versioning, payload bounds, and compensation.

Phase 65 is **not closed** until the repository-wide closure gate passes on the exact final `main` tree.

## Phase 66 — Advanced Web Control Plane

Dashboards, live activity, routing/health/cost/resources, DAGs, timelines/events/dependencies, logs/evidence/artifacts, code/Markdown/JSON/diff viewers, search, authorized controls, accessibility, and degraded-state UX.

## Phase 67 — Advanced TUI Control Center

Terminal-native cockpit for executions, tasks, agents, teams, workflows, models, providers, approvals, events, logs, evidence, artifacts, automation, health, live streams, trees, DAG/progress/timeline views, search/filtering, controls, reconnect, and degraded awareness.

## Phase 68 — Advanced CLI Platform

Run/task/agent/team/workflow/session/execution/approval/resume commands, logs/events/models/providers/status, profiles/config/auth, local/remote control, attachments, streaming, stable JSON/exit codes, CI/non-interactive operation, pipelines, and machine-readable errors/events.

## Phase 69 — npm Distribution + Setup

npm package/global CLI, one-command installation, platform/architecture detection, bootstrap/setup, OpenCode/OmniRoute detection/configuration, SI Core validation, diagnostics, upgrade/uninstall/migration, and clean-machine validation.

## Phase 70 — End-to-End Production Validation

Validate the complete OpenCode → SI → OmniRoute → provider/model → SI → OpenCode path across agents, teams, dependencies, reviews, fallback, limits, retries, cancellation, pause/resume, checkpoints, waits, approvals, restart/session/workspace recovery, security failures, context/cost limits, control surfaces, installation, upgrades, artifacts, evidence, telemetry, and evaluation.

## Phase 71 — Final Production Hardening

Final architecture, authority, state-machine, lifecycle, concurrency, idempotency, persistence, crash/restart, security, egress, tool/provider/runtime/context/scheduler/workspace/observability/UX/SDK/package/E2E audit with adversarial validation, performance/reliability, installation/upgrade, exact-tree, documentation, and final release evidence.

## Closure gate

A phase is not complete until implementation, unit/integration tests, adversarial/security tests, edge/failure tests, documentation synchronization, repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, and final exact-tree mainline CI are green.
