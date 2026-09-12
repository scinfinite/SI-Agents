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

V3 is closed. V4 has completed Phases **44–66**. Phases **46, 47, 49, 50, 58, 59, and 60** were advanced-hardened. **Phase 66 — Advanced Web Control Plane is closed at 100%. Phase 67 — Advanced TUI Control Center is next.**

## Closed phases

Phases 44–66 are closed under their recorded implementation, merge, documentation, and CI evidence.

### Phase 66 — Advanced Web Control Plane

**Complete / 100%.** Phase 66 provides a secure, accessible, same-origin operational web client over the existing WebServer and Control API. It covers dashboard/health, bounded live activity, workflows and DAG topology, timelines/events/dependencies, evidence, identity-bound approval visibility, governed run-request controls, resource/settings views, and code/Markdown/JSON/diff-oriented repository inspection with bounded search/filtering.

Implementation: `core/web/advanced.py`, `web/control/index.html`, `web/control/app.js`, and `web/control/styles.css`. The advanced handler is installed on the existing `WebServer` rather than creating a competing web authority.

The UI is a client of SI Core rather than a second authority. It inherits the established WebServer authentication/audit boundary, uses restrictive CSP and safe static/repository path resolution, has no third-party runtime dependency, and keeps streaming available through the existing API while using bounded polling for dashboard refresh. Governed run requests remain ordinary Control API requests and cannot bypass SI Core authorization.

Repository inspection is read-only, excludes `.git`, bounds source/diff payloads and search traversal, and uses timeout-bounded argument-vector Git inspection. Accessibility coverage includes keyboard navigation, skip links, semantic landmarks, status announcements, and non-color-only state labels.

Acceptance tests: `tests/unit/test_phase66_web_control.py` and `tests/unit/test_phase66_advanced_web.py`.

PR #79 merged successfully. Final synchronized-tree mainline CI **#1280** / run **34699748468** on commit `89e59f31c5785ab7a29aab8eec927cbebaa3b383` completed successfully. The SDK workflow on the same commit also completed successfully as run **34699748479**. This final synchronized-tree CI is the authoritative Phase 66 closure gate.

### Phase 65 — Workflow + Automation

Phase 65 delivers a transport-neutral declarative workflow engine with versioned DAG definitions, conditional branching, bounded loops and fan-out, delegation, human approval gates, durable waits, event/webhook/interval triggers, retries, runtime limits, cancellation, request-fingerprint-bound idempotency, durable JSON checkpoints, templates/importable definitions, restart validation, and reverse-order compensation.

Implementation: `core/automation/workflows.py`.

Verification: `tests/unit/test_phase65_workflows.py` and repository-wide CI. Final synchronized-tree CI #1249 / `34698187600` completed successfully with distribution build, wheel verification, repository audit, integration verification, Ruff, and full pytest all green.

## Phase 67 — Advanced TUI Control Center

**Next.** Terminal-native cockpit for executions, tasks, agents, teams, workflows, models, providers, approvals, events, logs, evidence, artifacts, automation, health, live streams, trees, DAG/progress/timeline views, search/filtering, controls, reconnect, and degraded awareness.

## Phase 68 — Advanced CLI Platform

Run/task/agent/team/workflow/session/execution/approval/resume commands, logs/events/models/providers/status, profiles/config/auth, local/remote control, attachments, streaming, stable JSON/exit codes, CI/non-interactive operation, pipelines, and machine-readable errors/events.

## Phase 69 — npm Distribution + Setup

npm package/global CLI, one-command installation, platform/architecture detection, bootstrap/setup, OpenCode/OmniRoute detection/configuration, SI Core validation, diagnostics, upgrade/uninstall/migration, and clean-machine validation.

## Phase 70 — End-to-End Production Validation

Validate the complete OpenCode → SI → OmniRoute → provider/model → SI → OpenCode path across agents, teams, dependencies, reviews, fallback, limits, retries, cancellation, pause/resume, checkpoints, waits, approvals, restart/session/workspace recovery, security failures, context/cost limits, control surfaces, installation, upgrades, artifacts, evidence, telemetry, and evaluation.

## Phase 71 — Final Production Hardening

Final architecture, authority, state-machine, lifecycle, concurrency, idempotency, persistence, crash/restart, security, egress, tool/provider/runtime/context/scheduler/workspace/observability/UX/SDK/package/E2E audit with adversarial validation, performance/reliability, installation/upgrade, exact-tree, documentation, and final release evidence.

## Closure gate

Phase 66 implementation, security/accessibility tests, repository validation, documentation synchronization, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, and final synchronized-tree mainline CI are green. **Phase 66 is therefore fully closed at 100%.**
