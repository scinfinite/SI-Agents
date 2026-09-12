# SI-Agents V4 Plan

## Authority and product architecture

SI-Agents V4 is a production-grade governed multi-agent orchestration platform built around **one authoritative SI Core**.

```text
User → OpenCode → SI Core / Control API
     → Scheduler / Orchestrator → Tasks / Agents / Teams / Workflows
     → Capability Authorization → OmniRoute → Models / Providers / APIs
     → Results / Artifacts / Evidence → SI Core
     → OpenCode / Web / TUI / CLI
```

OpenCode is a primary user-facing harness. OmniRoute is the model/provider/API routing layer. SI Core owns execution state, orchestration, governance, evidence, lifecycle, persistence, recovery, durable sessions, human gates, durable waiting, workspace lifecycle, observability, and evaluation. Integrations are adapters and never become competing business authorities.

## Current verified position

V3 is closed. V4 has completed Phases **44–60** in sequence at the required advanced-hardening level. Phases **46, 47, 49, and 50** were previously advanced-hardened; Phases **58, 59, and 60** have now received a dedicated advanced-hardening pass. **Phase 61 — Continuous Improvement is next.**

Phase 52 final exact-tree CI **#1020 (`34673411916`)**, Phase 53 final synchronized-tree CI **#1041 (`34675322458`)**, Phase 54 final synchronized-tree CI **#1051 (`34676632475`)**, Phase 55 synchronized-tree closure CI **#1080 (`34678317246`)**, Phase 56 final synchronized-tree mainline CI **#1099 (`34682849381`)**, Phase 57 final synchronized-tree mainline CI **#1113 (`34684260315`)**, and the Phase 58–60 advanced-hardening closure PR #74 / PR CI #1143 (`34691131729`) / final mainline CI #1144 (`34691176676`) all passed the repository distribution, wheel verification, repository audit, integration verification, Ruff, and full pytest gates.

### Phase 44 — Execution Runtime Foundation

Complete. Durable execution/attempt identity, canonical lifecycle transitions, idempotency, cancellation, pause/resume boundaries, deadlines, retry/new-attempt semantics, restart recovery, adapter isolation, terminality protection, and secret isolation.

Evidence: CI #919 / `34610448789`.

### Phase 45 — Event Bus + State Architecture

Complete. Durable append-only events, stable event identity, per-aggregate ordering, correlation/causation metadata, idempotent publication, replay, live subscriptions, durable projections/checkpoints, and authoritative runtime state.

Evidence: CI #935 / `34612616978`.

### Phase 46 — Parallel Scheduler + Executor — advanced hardened

Durable dependency-aware DAG scheduling, bounded parallel workers, fan-out/fan-in, priority/aging, cancellation/dependency propagation, restart recovery, EventBus integration, explicit execution identity checks, idempotent resubmission, conflict rejection, dependency-cycle defense, runtime-authoritative finalization, and security/authority boundaries.

Evidence: hardening CI #984 / `34671292491`.

### Phase 47 — OpenCode Bridge — advanced hardened

Health/session discovery, blocking/SSE invocation, per-request timeout propagation, bounded SSE frames, strict terminal semantics, cancellation, session filtering, correlation, error normalization, metadata allowlisting, loopback-default endpoint security, and SI Core authority.

Evidence: hardening CI #984 / `34671292491`.

### Phase 48 — OmniRoute Integration

Complete. Health/model discovery, capability-aware route selection, preferred/fallback candidates, OpenAI-compatible completions, streaming/non-streaming responses, usage normalization, upstream error classification, timeout handling, credential references, endpoint security, metadata allowlisting, and authority boundaries.

Evidence: CI #949 / `34623762921`.

### Phase 49 — Agent + Team Builder — advanced hardened

Immutable deterministic catalogs, schema-versioned manifests, definition/metadata validation, capability/model/resource declarations, bounded team composition, explicit handoffs, acyclic topology, deterministic execution layers, manifests/digests, declaration/runtime separation, and no implicit capability granting.

Evidence: hardening CI #984 / `34671292491`.

### Phase 50 — Capability Authorization — advanced hardened

Scoped grants and deny precedence, declared-capability enforcement, subject identity binding, fail-closed defaults, request-fingerprint-bound high/critical approvals, approval replay prevention, secret-like metadata rejection, bounded governance inputs, explicit/fail-closed egress, cost/risk controls, and deterministic non-secret evidence.

Evidence: hardening CI #984 / `34671292491`.

### Phase 51 — Checkpoints + Resume

Complete. Append-only SQLite checkpoints, ordered lineage, SHA-256 integrity, parent validation, secret-like rejection, bounded serialized state/metadata, durable reopen, terminal-only resume through new attempts, and optional EventBus facts. Checkpoints never restore authority, credentials, capabilities, grants, provider authorization, or identity.

Evidence: CI #977 / `34627956634`.

### Phase 52 — Context / Memory Economics — complete

Deterministic context and memory economics across user/project/session/workflow/team/task/agent scopes, relevance/importance ranking, normalized deduplication, model input-capacity enforcement, token/cost accounting, sensitive-context isolation, secret redaction/fail-closed dropping, deterministic compaction, summarizer hook, stable decision evidence, atomic snapshots, and adversarial coverage.

Evidence: final exact-tree CI #1020 / `34673411916`.

## Detailed V4 roadmap — Phases 53–71

Feature lists are planning scope, not claims of implementation. A phase becomes complete only after implementation, unit/integration tests, security/adversarial coverage, documentation synchronization, and final CI verification.

## Phase 53 — Persistent Sessions — complete

Durable session IDs/lifecycle/ownership; history/state; tasks/agents/teams/workflows/models/providers; artifacts/logs/evidence; token/cost history; context/memory; permissions/isolation; restart/recovery; expiration/archival; export/import; cloning/branching; replay; search/filtering; persistent OpenCode relationship; cross-interface continuity.

Delivered through SQLite-backed session storage and adapter contracts with isolation, optimistic revisions, ordered replay, artifact digests, expiry/archive, import/export, lineage, bounded search, restart recovery, and authority-preserving semantics.

Evidence: final synchronized-tree CI #1041 / `34675322458`.

## Phase 54 — Human-in-the-Loop — complete

Approval requests/gates, human input/review, risk/cost/egress/destructive/security/deployment approvals, escalation, pause/resume, reject/modify/retry/reassign/authorized alternatives, expiry, identity binding, audit/evidence, approval queues, shared Control API semantics, and fail-closed behavior. Human decisions remain governance evidence and never grant execution authority.

Evidence: final synchronized-tree CI #1051 / `34676632475`.

## Phase 55 — Durable Waiting + Scheduling — complete

Durable WAIT records, timer/delayed waits, recurring schedules, five-field UTC cron, event/resource/human/external wake-up, approval-compatible waiting, deadlines/timeouts, restart-safe waiting, queue priority and starvation resistance, and long-running workflows without occupying workers while waiting.

Implemented in `core/waiting` with SQLite persistence, explicit `waiting → ready → claimed → completed` lifecycle, terminal cancellation/expiry, ordered lifecycle events, optimistic revisions, bounded queue/payload limits, secret-like payload rejection, interval recurrence, bounded cron calculation, restart recovery, identity/project isolation, and Control API create/list/get/events/wake/claim/complete/cancel routes. A wait claim is an execution handoff only; downstream authorization remains mandatory.

Adversarial tests cover restart recovery, deadline expiry, wake-up, recurrence, cron validation, fairness/starvation, isolation, stale revisions, secret rejection, oversized payloads, idempotent cancellation, explicit claim lifecycle, JSON safety, and Control API round trips. Implementation CI #1074 (`34678184341`) and final synchronized-tree closure CI #1080 (`34678317246`) passed all required gates.

## Phase 56 — Intelligent Routing + Economics — complete

Task complexity/capability analysis; task/agent/model matching; capability/quality/latency/reliability/context-window/streaming/structured-output/vision/coding/reasoning/tool routing; cost-aware routing; preferred/fallback models/providers; health/history; escalation/downgrade; rate-limit/transient-failure handling; budgets; estimation/forecasting; retry economics; route evidence; circuit breakers/provider recovery. SI owns orchestration while OmniRoute owns model/provider/API routing.

Delivered through `core/provider_intelligence/intelligent_router.py`, with deterministic complexity inference, explicit task requirements, quality/reliability/latency/cost scoring, capability/context/output checks, provider/model preference, quota and circuit gating, budget reservations/settlement, retry forecasting, bounded transient/rate-limit fallback, escalation/downgrade controls, non-secret route evidence, health outcomes, recovery probes, and adversarial coverage. `ModelProfile` now includes quality plus streaming and structured-output capability declarations.

Evidence: PR #67 merged as `0c19e1c322b4262128b34a2203c54a30ece31f93`; PR verification CI #1091 (`34682603137`) passed; final synchronized-tree mainline CI #1099 (`34682849381`) passed all repository gates on final main tree.

## Phase 57 — Security Platform — complete

Established the single fail-closed security authority for SI Core: authenticated tenant identities; tenant-bound least-privilege subject/action/resource/scope grants; short-lived request-bound single-use capability tokens; tool/MCP/model/provider/filesystem/command/process/network authorization through explicit grants; secret isolation and redaction; workspace/project isolation; HTTPS egress allowlists with private-network protection; destructive/high-risk/credential approval enforcement; prompt/tool injection defenses; explicit trust boundaries; policy versioning; non-secret audit evidence; and adversarial tests. Security decisions are `ALLOW`, `DENY`, or `APPROVAL_REQUIRED`; approvals never become execution authority.

Implemented in `core/security/platform.py` and exported through `core/security`. Verification covers identity/tenant isolation, least privilege, bounded scopes, approvals, egress/private-network controls, credential/egress separation, secret scanning, injection rejection, HMAC token binding/replay prevention/TTL/policy invalidation, expired grants, trust-boundary non-authority, and safe audit evidence. PR #68 merged as `26e001bc3756fb28ecbc9773db8df6a46d26dba7`; final synchronized-tree mainline CI #1113 (`34684260315`) passed all repository gates on final `main`.

## Phase 58 — Workspace / Worktree Lifecycle — advanced hardened

Workspace/Git worktree/branch lifecycle, isolation, ownership/locking, dirty/conflict detection, diff/patch/merge preparation, artifacts, snapshots/checkpoints, cleanup/recovery, authorized resume, permissions/audit history, and garbage collection. Advanced hardening added adversarial lifecycle-event tamper detection and sensitive-operation authorization callback coverage.

Evidence: PR #74 / CI #1143 (`34691131729`); final mainline CI #1144 (`34691176676`).

## Phase 59 — Observability — advanced hardened

Durable structured logs/events/metrics/spans, tenant/project scope, secret redaction and shared scanner detection, bounded payload/resource limits, correlation/causation, trace timelines, live-feed retention, percentile metrics, operator health, JSONL export, and integrity evidence. Advanced hardening verifies tampering beyond the first query page and tightens resource/severity contracts.

Evidence: PR #74 / CI #1143 (`34691131729`); final mainline CI #1144 (`34691176676`).

## Phase 60 — Evaluation + Benchmarking — advanced hardened

Deterministic golden cases and multi-mode scoring, reliability/security/latency/cost dimensions, failure classification, benchmark history, regression detection, human review, weighted experiments, evidence digests, and release gating. Advanced hardening makes cost/latency budgets enforceable, rejects secret-bearing evaluator outputs/metadata/review rationale, verifies persisted evidence integrity, tightens experiment inputs, and fails closed on empty reports.

Evidence: PR #74 / CI #1143 (`34691131729`); final mainline CI #1144 (`34691176676`).

## Phase 61 — Continuous Improvement

Failure analysis/clustering, regression detection, optimization recommendations, agent/team/model/routing/workflow improvement, cost/reliability/performance optimization, experiments, canaries, rollback, human approval for consequential changes, and evidence/history.

## Phase 62 — Cross-Runtime / Cross-Harness

Runtime/session/tool/model/event/capability/context/checkpoint/artifact adapters, common contracts, capability discovery/health/selection/fallback, harness-neutral state, runtime-specific isolation, and first-class OpenCode integration without making SI Core OpenCode-dependent.

## Phase 63 — Ecosystem / Marketplace

Governed agents/skills/tools/teams/workflows/model/provider profiles/MCP/extensions, manifests, versions/dependencies/compatibility, capability/permission declarations, security/provenance/trust, install/update/uninstall/rollback, drift detection, registries, templates, and governance gates.

## Phase 64 — SDK / Developer Platform

Python and TypeScript/JavaScript SDKs, versioned REST/WebSocket/SSE, typed schemas, stable errors, auth, idempotency, concurrency, pagination/filtering, webhooks/event subscriptions, CI/CD integration, examples, and reference tooling.

## Phase 65 — Workflow + Automation

Sequential/parallel/conditional/loop/fan-out/fan-in/dynamic DAGs, agent/team delegation, human gates, durable waits/timers/schedules, event triggers, retry/failure branches, compensation/rollback, checkpoints/resume, versioning/templates/import/export/visualization, and developer-tool integrations.

## Phase 66 — Advanced Web Control Plane

Rich localhost-first control: dashboards, live activity, routing/health/cost/resources, interactive DAGs, timelines/events/dependencies, logs/evidence/artifacts, code/Markdown/JSON/diff viewers, search/navigation, command palette, authorized controls, themes, responsive/accessibility support, and state/error/degraded UX.

## Phase 67 — Advanced TUI Control Center

Terminal-native dashboard/operator cockpit for executions, tasks, agents, teams, workflows, models, providers, approvals, events, logs, evidence, artifacts, automation and health with live streams, split panes, trees, DAG/progress/timeline views, search/filtering, controls, reconnect, and degraded awareness.

## Phase 68 — Advanced CLI Platform

Run/task/agent/team/workflow/session/execution/approval/resume commands; logs/events/models/providers/status; interactive selection/completion; profiles/config/auth; local/remote control; attachment; streaming; stable JSON/exit codes; CI/non-interactive operation; pipelines; machine-readable errors/events.

## Phase 69 — npm Distribution + Setup

npm package/global CLI, one-command installation, platform/architecture detection, bootstrap/setup wizard, OpenCode/OmniRoute detection/configuration, SI Core validation, diagnostics/health, upgrade/uninstall/migration, and clean-machine validation.

## Phase 70 — End-to-End Production Validation

Validate the full OpenCode → SI → OmniRoute → provider/model → SI → OpenCode path across agents, teams, dependencies, reviews, fallback, limits, timeouts, retries, cancellation, pause/resume, checkpoints, durable waits, approvals, restart/session/workspace recovery, authorization/security failures, context/cost limits, large workflows, all control surfaces, installation, upgrades, artifacts, evidence, telemetry, and evaluation.

## Phase 71 — Final Production Hardening

Final architecture/authority/state-machine/lifecycle/concurrency/idempotency/persistence/crash/restart/security/egress/tool/provider/runtime/context/scheduler/workspace/observability/UX/SDK/package/E2E audit, including adversarial validation, performance/reliability, installation/upgrade, exact-tree, documentation, and final mainline CI release evidence.

## External engineering references

External engineering reference systems are used for pattern research only. Useful patterns are generalized into SI-Agents contracts and tests rather than copied as dependencies, prompts, or authorities. SI Core remains the sole business authority.

## Interface contract

Web, TUI, CLI, and OpenCode operate against the same SI Core authority. No interface creates competing execution, session, approval, or waiting state ownership.
