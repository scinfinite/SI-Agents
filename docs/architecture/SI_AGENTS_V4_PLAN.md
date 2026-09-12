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

V3 is closed. V4 has completed Phases **44–65**. Phases **46, 47, 49, 50, 58, 59, and 60** were advanced-hardened. **Phase 66 — Advanced Web Control Plane is active.**

## Closed phases

Phases 44–65 are closed under their recorded implementation, merge, documentation, and CI evidence.

### Phase 65 — Workflow + Automation

Phase 65 delivers a transport-neutral declarative workflow engine with versioned DAG definitions, conditional branching, bounded loops and fan-out, delegation, human approval gates, durable waits, event/webhook/interval triggers, retries, runtime limits, cancellation, request-fingerprint-bound idempotency, durable JSON checkpoints, templates/importable definitions, restart validation, and reverse-order compensation.

Implementation: `core/automation/workflows.py`.

Verification: `tests/unit/test_phase65_workflows.py` and repository-wide CI. Final synchronized-tree CI #1249 / `34698187600` completed successfully with distribution build, wheel verification, repository audit, integration verification, Ruff, and full pytest all green.

## Phase 66 — Advanced Web Control Plane

**Active.** Phase 66 provides a secure, accessible, same-origin operational web client over the versioned Control API. It covers dashboards and health, live activity, routing/health/cost/resource read models, workflows and DAG topology, timelines/events/dependencies, evidence, code/Markdown/JSON/diff-oriented inspection surfaces, search/filtering, identity-bound authorized controls, accessibility, and degraded-state UX.

Implementation: `core/control_api/web.py`, `web/control/index.html`, `web/control/app.js`, and `web/control/styles.css`.

The UI is a client of SI Core rather than a second authority. It inherits the API's localhost-first and authentication boundaries, uses restrictive CSP and safe static-path resolution, has no third-party runtime dependency, and keeps streaming available through the existing API while using bounded polling for dashboard refresh.

Acceptance tests: `tests/unit/test_phase66_web_control.py`.

Documentation: `docs/architecture/PHASE_66_ADVANCED_WEB_CONTROL_PLANE.md`.

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

A phase is not complete until implementation, unit/integration tests, adversarial/security tests, edge/failure tests, documentation synchronization, repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, and final exact-tree mainline CI are green. **Phase 65 satisfies this gate; Phase 66 does not yet.**
