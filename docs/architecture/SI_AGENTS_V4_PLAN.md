# SI-Agents V4 Plan

## Authority

SI-Agents V4 is built around one authoritative SI Core. Web, TUI, CLI, OpenCode, runtime adapters, schedulers, agents, teams, workflows, and integrations are clients/adapters, not competing state authorities.

```text
User → OpenCode / Web / TUI / CLI → SI Core / Control API
     → Scheduler / Orchestrator → Tasks / Agents / Teams / Workflows
     → Capability Authorization → OmniRoute → Models / Providers / APIs
     → Results / Artifacts / Evidence → SI Core
     → Observability → Evaluation → Continuous Improvement
     → Cross-Runtime → Release Gates / Canaries / Rollback → Clients
```

OmniRoute owns model/provider/API routing. SI Core owns execution, orchestration, governance, evidence, lifecycle, persistence, recovery, waiting, workspaces, observability, evaluation, and improvement governance.

## Current verified position

V3 is closed. V4 has completed Phases **44–62**. Phases **46, 47, 49, 50, 58, 59, and 60** were advanced-hardened. **Phase 62 — Cross-Runtime / Cross-Harness is complete: implementation, adversarial verification, documentation synchronization, merge, and mainline CI closure are green. Phase 63 — Ecosystem / Marketplace follows.**

## Closed phases

Phases 44–62 are closed under their recorded CI evidence. Phase 62 merged as PR #76 (`607085782a75e31a60774afe975edcbd38bf5e4c`) with PR CI #1166 (`34692621358`) green and mainline CI #1180 (`34693460152`) green on the integration-marker correction.

### Phase 62 — Cross-Runtime / Cross-Harness

Phase 62 establishes harness-neutral interoperability across runtime/session/tool/model/event/capability/context/checkpoint/artifact resource families. It provides common portable adapter contracts, deterministic harness discovery, capability filtering, health probing, bounded quarantine/recovery, preferred selection, project+harness session binding, explicit migration, and safe pre-start fallback.

The gateway refuses fallback after execution-start signals, keeps routing evidence non-secret, and fails closed when no eligible harness exists. It never grants capabilities or mutates SI Core execution state. OpenCode remains a supported harness rather than the runtime definition.

Implementation: `core/runtime/cross_runtime.py` and `core/runtime/portable.py`.

Verification: `tests/unit/test_phase62_cross_runtime.py`, PR CI #1166, and mainline CI #1180. The final documentation-synchronized exact-tree mainline CI is the last closure gate for this documentation update.

## Phase 63 — Ecosystem / Marketplace — next

Governed agents, skills, tools, teams, workflows, model/provider profiles, MCP extensions, manifests, versions, dependencies, compatibility, permission declarations, provenance/trust, install/update/uninstall/rollback, drift detection, registries, templates, and governance gates.

## Phase 64 — SDK / Developer Platform

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
