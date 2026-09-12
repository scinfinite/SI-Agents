# SI-Agents V4 Plan

## Authority

SI-Agents V4 is built around one authoritative SI Core. Web, TUI, CLI, OpenCode, runtime adapters, schedulers, agents, teams, workflows, and integrations are clients/adapters, not competing state authorities.

```text
User → OpenCode / Web / TUI / CLI → SI Core / Control API
     → Scheduler / Orchestrator → Tasks / Agents / Teams / Workflows
     → Capability Authorization → OmniRoute → Models / Providers / APIs
     → Results / Artifacts / Evidence → SI Core
     → Observability → Evaluation → Continuous Improvement
     → Release Gates / Canaries / Rollback → Clients
```

OmniRoute owns model/provider/API routing. SI Core owns execution, orchestration, governance, evidence, lifecycle, persistence, recovery, waiting, workspaces, observability, evaluation, and improvement governance.

## Current verified position

V3 is closed. V4 has completed Phases **44–62**. Phases **46, 47, 49, 50, 58, 59, and 60** were advanced-hardened. **Phase 62 — Cross-Runtime / Cross-Harness is fully closed. Phase 63 — Ecosystem / Marketplace is next.**

## Closed phases

### Phase 44 — Execution Runtime Foundation

Durable execution/attempt identity, canonical lifecycle, idempotency, cancellation, pause/resume, deadlines, retry/new-attempt semantics, restart recovery, adapter isolation, terminality protection, and secret isolation.

Evidence: CI #919 / `34610448789`.

### Phase 45 — Event Bus + State Architecture

Durable append-only events, stable event identity, ordering, correlation/causation, idempotent publication, replay, subscriptions, projections/checkpoints, and authoritative runtime state.

Evidence: CI #935 / `34612616978`.

### Phase 46 — Parallel Scheduler + Executor — advanced hardened

Dependency-aware DAG scheduling, bounded workers, fan-out/fan-in, priority/aging, cancellation/dependency propagation, restart recovery, EventBus integration, execution identity checks, idempotent resubmission, conflict/cycle defense, runtime-authoritative finalization.

Evidence: hardening CI #984 / `34671292491`.

### Phase 47 — OpenCode Bridge — advanced hardened

Health/session discovery, blocking/SSE invocation, timeout propagation, bounded frames, terminal semantics, cancellation, session filtering, correlation, error normalization, metadata allowlisting, endpoint security, and SI Core authority.

Evidence: hardening CI #984 / `34671292491`.

### Phase 48 — OmniRoute Integration

Capability-aware model/provider routing, preferred/fallback candidates, OpenAI-compatible invocation, streaming/non-streaming responses, usage normalization, upstream error classification, timeouts, credential references, endpoint security, and authority boundaries.

Evidence: CI #949 / `34623762921`.

### Phase 49 — Agent + Team Builder — advanced hardened

Immutable deterministic catalogs, manifests, validation, capability/model/resource declarations, bounded team composition, explicit handoffs, acyclic topology, deterministic execution layers, and declaration/runtime separation.

Evidence: hardening CI #984 / `34671292491`.

### Phase 50 — Capability Authorization — advanced hardened

Scoped grants, deny precedence, subject binding, fail-closed defaults, request-bound approvals, replay prevention, secret rejection, bounded governance inputs, egress controls, cost/risk controls, and deterministic evidence.

Evidence: hardening CI #984 / `34671292491`.

### Phase 51 — Checkpoints + Resume

Append-only checkpoints, ordered lineage, SHA-256 integrity, parent validation, secret rejection, bounded state, durable reopen, terminal-only resume, and authority-preserving semantics.

Evidence: CI #977 / `34627956634`.

### Phase 52 — Context / Memory Economics

Deterministic context budgets, relevance/importance selection, deduplication, model capacity enforcement, token/cost accounting, sensitive-context isolation, secret handling, compaction, summarization hooks, atomic snapshots, and adversarial coverage.

Evidence: CI #1020 / `34673411916`.

### Phase 53 — Persistent Sessions

Durable session ownership/history/state, task/agent/team/workflow relationships, artifacts/evidence, context/memory, permissions/isolation, restart/recovery, expiry/archive, import/export, cloning/branching, replay, search, and cross-interface continuity.

Evidence: CI #1041 / `34675322458`.

### Phase 54 — Human-in-the-Loop

Approval gates, human input/review, escalation, pause/resume, expiry, identity binding, audit/evidence, queues, and fail-closed governance semantics. Human decisions never grant execution authority.

Evidence: CI #1051 / `34676632475`.

### Phase 55 — Durable Waiting + Scheduling

Durable waits, timers, recurring schedules, UTC cron, event/resource/human/external wake-up, approval-compatible waiting, deadlines, restart-safe waiting, fairness, and long-running workflows without occupying workers.

Evidence: CI #1080 / `34678317246`.

### Phase 56 — Intelligent Routing + Economics

Complexity/capability matching, quality/latency/reliability/context/streaming/structured-output routing, cost-aware selection, health/quota/circuit controls, budgets, retry economics, escalation/downgrade, and route evidence.

Evidence: CI #1099 / `34682849381`.

### Phase 57 — Security Platform

Tenant identity, least privilege, scoped grants, short-lived request-bound tokens, tool/MCP/model/provider/filesystem/command/process/network authorization, secret isolation, workspace isolation, egress/private-network controls, high-risk approvals, injection defense, policy versioning, and non-secret audit evidence.

Evidence: CI #1113 / `34684260315`.

### Phases 58–60 — Advanced-hardening closure

Workspace/worktree lifecycle, observability, and evaluation/benchmarking were advanced-hardened together: lifecycle tamper evidence, authorization callbacks, deep secret/resource defenses, complete integrity scanning, enforceable cost/latency release budgets, persisted evidence verification, strict experiment validation, and fail-closed evaluation reporting.

Evidence: PR #74 / CI #1143 (`34691131729`); final mainline CI #1144 (`34691176676`).

### Phase 61 — Continuous Improvement

Failure clustering, regression signals, explainable recommendations, deterministic experiments, fail-closed canary gates, consequential-change approval binding, rollback planning, secret rejection, and tamper-evident improvement history.

Evidence: PR #75 / CI #1157 (`34692165853`).

### Phase 62 — Cross-Runtime / Cross-Harness

Phase 62 establishes harness-neutral interoperability across runtime/session/tool/model/event/capability/context/checkpoint/artifact resource families. It provides common portable adapter contracts, deterministic harness discovery, capability filtering, health probing, bounded quarantine/recovery, preferred selection, project+harness session binding, explicit migration, and safe pre-start fallback.

The gateway refuses fallback after execution-start signals, keeps routing evidence non-secret, and fails closed when no eligible harness exists. It never grants capabilities or mutates SI Core execution state. OpenCode remains a supported harness rather than the runtime definition.

Implementation: `core/runtime/cross_runtime.py` and `core/runtime/portable.py`.

Verification: `tests/unit/test_phase62_cross_runtime.py`, plus the complete repository CI closure suite. PR and final mainline CI are the closure gate.

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
