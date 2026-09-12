# SI-Agents V4 Plan

## Authority

SI-Agents V4 is built around one authoritative SI Core. Web, TUI, CLI, OpenCode, runtime adapters, schedulers, agents, teams, workflows, and integrations are clients/adapters, not competing state authorities.

```text
User → OpenCode / Web / TUI / CLI → SI Core / Control API
     → Scheduler / Orchestrator → Tasks / Agents / Teams / Workflows
     → Capability Authorization → OmniRoute → Models / Providers / APIs
     → Results / Artifacts / Evidence → SI Core
     → Observability → Evaluation → Continuous Improvement
     → Cross-Runtime → Ecosystem / Marketplace → Release Gates / Canaries / Rollback → Clients
```

OmniRoute owns model/provider/API routing. SI Core owns execution, orchestration, governance, evidence, lifecycle, persistence, recovery, waiting, workspaces, observability, evaluation, and improvement governance.

## Current verified position

V3 is closed. V4 has completed Phases **44–63**. Phases **46, 47, 49, 50, 58, 59, and 60** were advanced-hardened. **Phase 62 — Cross-Runtime / Cross-Harness and Phase 63 — Ecosystem / Marketplace are complete: implementation, adversarial verification, documentation synchronization, merge, and mainline CI closure are green. Phase 64 — SDK / Developer Platform follows.**

## Closed phases

Phases 44–63 are closed under their recorded CI evidence. Phase 62 merged as PR #76 (`607085782a75e31a60774afe975edcbd38bf5e4c`) with final mainline CI #1186 (`34693756693`) green.

### Phase 63 — Ecosystem / Marketplace

Phase 63 establishes governed ecosystem metadata and lifecycle contracts for future agents, skills, tools, teams, workflows, model/provider profiles, and MCP extensions. `MarketplaceManifest` provides strict semver, dependencies, compatibility declarations, permission declarations, provenance/trust, payload identity, and exact manifest identity. `MarketplaceRegistry` provides deterministic package/version lookup and templates. `EcosystemManager` provides governed install/update/uninstall/rollback, bounded lifecycle history, and drift detection.

The lifecycle layer is governance-neutral and does not execute package payloads or grant capabilities. Untrusted packages require an explicit governance hook, requested permissions must be declared, dependency requirements must be satisfied, and governance approval is bound to the exact manifest digest. SI Core remains authoritative for authorization and execution.

Implementation: `core/marketplace/registry.py` and `core/marketplace/__init__.py`.

Verification: `tests/unit/test_phase63_marketplace.py`, PR #77 / CI #1189 (`34694186010`), and the final synchronized-tree mainline closure suite.

## Phase 64 — SDK / Developer Platform — next

Python and TypeScript/JavaScript SDKs, versioned REST/WebSocket/SSE, typed schemas, stable errors, auth, idempotency, concurrency, pagination/filtering, webhooks/event subscriptions, CI/CD integration, examples, and reference tooling.

## Phase 65 — Workflow + Automation

Sequential/parallel/conditional/loop/fan-out/fan-in/dynamic DAGs, delegation, human gates, durable waits/timers/schedules, event triggers, retry/failure branches, compensation/rollback, checkpoints/resume, versioning/templates/import/export, and developer integrations.

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
