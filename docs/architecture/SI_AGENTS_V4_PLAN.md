# SI-Agents V4 Plan

## V4 product vision

SI-Agents V4 is a production-grade, governed, persistent, observable, multi-agent orchestration platform built around **one authoritative SI Core**.

The intended primary flow is:

```text
User prompt → OpenCode → SI OpenCode Bridge → SI Core / Control API
→ Scheduler / Orchestrator → Tasks / Agents / Teams / Workflows
→ Capability Authorization → OmniRoute → Models / Providers / APIs
→ Results / Artifacts / Evidence → SI Core → OpenCode / Web / TUI / CLI
```

**Authority boundary:** OpenCode is a primary user-facing coding harness; OmniRoute is the model/provider/API routing layer; SI Core owns execution state, orchestration, governance, evidence, lifecycle, persistence, and recovery. External runtimes/providers are adapters and never become authoritative state owners.

## Current verified position

V3 is closed. V4 implementation has completed Phases 44–52 in sequence. Phases 46, 47, 49, and 50 subsequently passed advanced-level hardening without reopening the phase sequence. **Phase 52 — Context / Memory Economics is complete on main. Phase 53 — Persistent Sessions is next.**

Advanced audit CI **#984 (`34671292491`)** passed distribution, wheel verification, repository audit, integration verification, Ruff, and the complete pytest suite. Phase 52 mainline CI **#1015 (`34673115687`)** passed distribution build, wheel installation verification, repository audit, integration verification, Ruff, and the full test suite on merge commit `215dd5491b4e6f38f454faaf5b0a2f8331694455`. The documentation-closure merge requires one final exact-tree mainline CI after these synchronized status documents land.

### Phase 44 — Execution Runtime Foundation

Complete. Durable execution/attempt identity, canonical lifecycle transitions, idempotency, cancellation, pause/resume boundaries, deadlines, retry/new-attempt semantics, restart recovery, adapter isolation, terminality protection, and secret isolation.

Evidence: CI #919 / `34610448789`.

### Phase 45 — Event Bus + State Architecture

Complete. Durable append-only events, stable event identity, per-aggregate ordering, correlation/causation metadata, idempotent publication, replay, live subscriptions, durable projections/checkpoints, and authoritative runtime state.

Evidence: CI #935 / `34612616978`.

### Phase 46 — Parallel Scheduler + Executor — advanced hardened

Durable dependency-aware DAG scheduling, bounded parallel workers, fan-out/fan-in, priority/aging, cancellation and dependency propagation, restart recovery, EventBus integration, explicit execution identity checks, idempotent matching resubmission, conflict rejection, dependency-cycle defense, runtime-authoritative finalization, and security/authority boundaries.

Evidence: hardening CI #984 / `34671292491`.

### Phase 47 — OpenCode Bridge — advanced hardened

Health/session discovery, blocking and SSE invocation, per-request transport timeout propagation, bounded 1 MiB SSE frames, strict terminal semantics, cancellation, session filtering, request/session correlation, error normalization, metadata allowlisting, loopback-default endpoint security, and SI Core authority.

Evidence: hardening CI #984 / `34671292491`.

### Phase 48 — OmniRoute Integration

Complete. Health/model discovery, capability-aware route selection, preferred/fallback candidates, OpenAI-compatible completions, streaming/non-streaming responses, usage normalization, upstream error classification, timeout handling, credential references, loopback-default endpoint security, metadata allowlisting, and explicit authority boundaries.

Evidence: CI #949 / `34623762921`.

### Phase 49 — Agent + Team Builder — advanced hardened

Immutable definitions and deterministic catalogs, schema-versioned manifests, duplicate/metadata validation, capability/model/resource declarations, bounded team composition, explicit handoffs, acyclic topology, deterministic topological execution layers, manifests/digests, declaration/runtime authority separation, and no implicit capability granting.

Evidence: hardening CI #984 / `34671292491`.

### Phase 50 — Capability Authorization — advanced hardened

Scoped grants and deny precedence, declared-capability enforcement, subject identity binding, fail-closed defaults, request-fingerprint-bound high/critical approvals, approval replay prevention, secret-like metadata rejection, bounded governance inputs, explicit/fail-closed egress, cost/risk controls, and deterministic non-secret authorization evidence.

Evidence: hardening CI #984 / `34671292491`.

### Phase 51 — Checkpoints + Resume

Complete. Append-only SQLite checkpoints, ordered lineage, SHA-256 integrity, parent validation, secret-like field rejection, bounded serialized state/metadata, durable reopen, terminal-only resume through `ExecutionStore.new_attempt()`, and optional EventBus facts. Checkpoints preserve progress evidence but never restore authority, credentials, capabilities, grants, provider authorization, or identity.

Evidence: CI #977 / `34627956634`.

### Phase 52 — Context / Memory Economics — complete

Implemented deterministic context and memory economics across user/project/session/workflow/team/task/agent scopes. `core/context_economics/` provides context item/budget/model-profile/selection contracts, deterministic relevance/importance ranking, normalized-content deduplication, model input-capacity enforcement, token/cost accounting, sensitive-context isolation, default secret redaction or fail-closed dropping, deterministic compaction, an explicit summarizer hook, stable decision evidence, and atomic snapshots. The layer remains below authorization and orchestration authority.

Security/adversarial coverage includes invalid budgets, duplicate amplification, sensitive-context isolation, secret leakage attempts, overflow/compaction, cost ceilings, summarization behavior, snapshot serialization/schema rejection, deterministic ordering, and failure handling.

Evidence: PR CI #1014 on the final branch, followed by mainline CI #1015 (`34673115687`) on merge commit `215dd5491b4e6f38f454faaf5b0a2f8331694455`.

## Detailed V4 roadmap — Phases 53–71

Feature lists are planning scope, not claims of implementation. A phase becomes complete only after implementation, unit/integration tests, security/adversarial coverage, documentation synchronization, and final CI verification.

## Phase 53 — Persistent Sessions

Durable session IDs/lifecycle/ownership; history/state; tasks/agents/teams/workflows/models/providers; artifacts/logs/evidence; token/cost history; context/memory; permissions/isolation; recovery/restart; expiration/archival; export/import; cloning/branching; replay; search/filtering; persistent OpenCode relationship; cross-interface continuity.

## Phase 54 — Human-in-the-Loop

Approval requests/gates; human input/review; risk/cost/egress/destructive/security/deployment approvals; escalation; pause/resume; reject/modify/retry/reassign/authorized alternatives; expiry; identity binding; audit/evidence; notifications; approval queues; Web/TUI/CLI controls; fail-closed behavior.

## Phase 55 — Durable Waiting + Scheduling

Durable WAIT; timers; delayed/recurring execution; cron-like schedules; wake-up/event triggers; approval/human/dependency/resource/external waits; deadlines/timeouts; retry backoff/jitter; restart-safe waiting; queue priority/fairness/starvation prevention; calendar execution; long-running workflows without occupying workers while waiting.

## Phase 56 — Intelligent Routing + Economics

Task complexity/capability analysis; task/agent/model matching; capability/quality/latency/reliability/context-window/streaming/structured-output/vision/coding/reasoning/tool routing; cost-aware routing; preferred/fallback models/providers; health/history; escalation/downgrade; rate-limit/transient-failure handling; budgets; estimation/forecasting; retry economics; route evidence; circuit breakers/provider recovery. SI owns orchestration while OmniRoute owns model/provider/API routing.

## Phase 57 — Security Platform

Least privilege, identities, scoped permissions/capability tokens, tool/MCP/model/provider/filesystem/command/process/network authorization, secret references/isolation/redaction, workspace/project isolation, egress controls, destructive-operation controls, approval enforcement, audit/evidence, prompt/tool/context injection defenses, agent trust boundaries, security/supply-chain/configuration scanning, adversarial policy tests, policy versioning, fail-closed defaults.

## Phase 58 — Workspace / Worktree Lifecycle

Workspace and Git worktree/branch lifecycle, per-agent/task/team isolation, authorized shared workspaces, locking/ownership, dirty-worktree/conflict detection, diff/patch/merge preparation, artifact collection, snapshots/checkpoints, cleanup/recovery, authorized resume, permission/audit history, abandoned-workspace garbage collection.

## Phase 59 — Observability

Live execution/task/agent/team/workflow state; queue/running/waiting/approval/retry/checkpoint/failure status; token/cost/latency/throughput/resource metrics; handoffs/dependencies/DAG progress/critical path/bottlenecks; structured logs/metrics/traces; correlation/causation IDs; execution/provider/cost/error/evidence timelines; tool/model calls; artifact/diff inspection; search/filter/debug/audit; telemetry export; operator health/incident views.

## Phase 60 — Evaluation + Benchmarking

Agent/team/workflow/model/provider/routing/tool evaluations; security/reliability/cost/latency/quality benchmarks; scenarios; golden tasks/outputs; expected behavior; automated/human evaluation; scoring/failure classification; datasets/reports; historical/version comparisons; A/B experiments; regression detection; release gates; evidence-backed results.

## Phase 61 — Continuous Improvement

Failure analysis/clustering; regression detection; agent/team/model/routing/workflow analysis; optimization recommendations; prompt/skill/agent/routing/workflow improvement; cost/reliability/performance optimization; experiment tracking/versioning; canaries; rollback; human approval for consequential changes; evidence/history. Core loop: execute → observe → evaluate → diagnose → improve → test → deploy → observe.

## Phase 62 — Cross-Runtime / Cross-Harness

Runtime/session/tool/model/event/capability/context/checkpoint/artifact adapters; common execution/task/agent/event/capability/session/artifact contracts; runtime capability discovery/health/selection/fallback; harness-neutral state; runtime-specific isolation; OpenCode first-class integration without making SI Core OpenCode-dependent.

## Phase 63 — Ecosystem / Marketplace

Governed agents/skills/tools/teams/workflows/model/provider profiles/MCP/extensions; manifests; versions/dependencies/compatibility; capability/permission declarations; security scanning; provenance/signatures/trust where supported; install/update/uninstall/rollback; drift detection; local/private and official/community registries; templates; governance gates.

## Phase 64 — SDK / Developer Platform

Python and TypeScript/JavaScript SDKs; versioned REST/WebSocket/SSE; control/execution/task/agent/team/workflow/session/event/artifact/approval/evaluation/observability APIs; typed schemas; stable errors; authentication/authorization; idempotency; concurrency controls; pagination/filtering; webhooks/event subscriptions; CI/CD integration; examples/reference docs/tooling.

## Phase 65 — Workflow + Automation

Sequential/parallel/conditional/loop/fan-out/fan-in/dynamic DAGs; agent/team delegation; human gates; durable waits/timers/schedules; webhooks/event triggers; retry/failure branches; compensation/rollback; checkpoints/resume; versioning/templates/import/export/visualization; Git/GitHub, CI/CD, issue tracker, chat, APIs, webhooks, MCP, filesystem and developer-tool integrations.

## Phase 66 — Advanced Web Control Plane

Rich localhost-first Web control: live dashboard, execution/task/agent/team activity, routing/health/cost/resources, interactive DAG/workflow canvas, timelines/events/dependencies, logs/evidence/artifacts, code/Markdown/JSON/diff viewers, previews, search/navigation, command palette, keyboard shortcuts, authorized controls, themes, responsive layouts, accessibility, skeleton/empty/error states, meaningful state animations, and control of CLI/TUI/OpenCode work through shared SI Core.

## Phase 67 — Advanced TUI Control Center

Terminal-native dashboard/operator cockpit for executions, tasks, agents, teams, workflows, models, providers, approvals, events, logs, evidence, artifacts, automation and system health; live streams, split panes, trees, DAG/progress/timeline views, fuzzy search, filtering/sorting, keyboard navigation, inspection, approvals, controls, reconnect and degraded/offline awareness.

## Phase 68 — Advanced CLI Platform

Run/task/agent/team/workflow/session/execution/approval/resume commands; logs/events/models/providers/status; interactive selection/completion/context-aware commands; profiles/config/auth; local/remote control; attachment; streaming; stable JSON schemas and exit codes; CI/non-interactive mode; quiet/verbose/debug; Unix pipelines; machine-readable errors/events.

## Phase 69 — npm Distribution + Setup

npm package/global CLI, one-command installation, startup, platform/architecture detection, Linux/macOS/Windows and ARM/x64 where dependencies permit, bootstrap, setup wizard, OpenCode/OmniRoute detection/configuration, SI Core validation, Web/TUI/CLI availability, diagnostics, health checks, upgrade/uninstall/migration, clean-machine validation.

## Phase 70 — End-to-End Production Validation

Validate OpenCode → SI → OmniRoute → model/provider → SI → OpenCode across single/multiple/parallel agents, teams, handoffs, dependencies, reviews, fallback, rate limits, timeouts, retries, circuit breakers, cancellation, pause/resume, checkpoints, durable waits, approvals, restart/session/workspace recovery, authorization violations, secret leakage, prompt/tool/context injection, context/cost limits, long/large workflows, Web/TUI/CLI control, installation/upgrade/clean setup, cross-runtime behavior, artifacts/evidence/telemetry/evaluation.

## Phase 71 — Final Production Hardening

Final architecture/authority/state-machine/lifecycle/concurrency/race/idempotency/stale-state/persistence/crash/restart/partial-execution audit; authorization/secrets/network egress/tools/supply-chain; OpenCode/OmniRoute/runtime/provider failures; context/memory economics; scheduler/workflow; workspace; observability/evidence; Web/TUI/CLI UX/accessibility/reconnect/degraded modes; SDK/API/schema stability; npm installation/upgrade/migration. Adversarial validation covers duplicate requests/events, concurrent conflicts, lost connections, provider/runtime/persistence failures, authorization replay/privilege escalation, secret/metadata/prompt/tool/context injection, resource exhaustion, load/performance, and complete E2E. Release evidence must include repository audit, distribution/package/wheel verification, integration, Ruff, compileall, full pytest, security/adversarial, E2E, performance/reliability, installation/upgrade, exact-tree, documentation verification, and final mainline CI.

## External engineering references

External engineering reference systems are used for pattern research only. Useful patterns are generalized into SI-Agents contracts and tests rather than copied as dependencies, prompts, or authorities. SI Core remains the sole business authority.

## Interface vision

### Web

The localhost Web interface is the intended richest SI control plane: live system/execution status; task/agent/team activity; workflow/DAG visualization; event streams; timelines; logs; evidence; artifacts; code/Markdown/JSON/diff viewers; route/model/provider health; token/cost/resource metrics; approvals; pause/resume/stop/retry/cancel controls; search/global navigation; command palette; keyboard shortcuts; responsive layouts; themes; accessibility; skeleton/empty/error states; confirmations; and meaningful state animations/transitions.

### TUI

The TUI is a terminal-native operator cockpit: dashboard, executions, tasks, agents, teams, workflows, models, providers, approvals, events, logs, evidence, artifacts, automation, system health, live refresh/streaming, split panes, trees, DAG/progress/timeline views, fuzzy search, filtering/sorting, JSON/diff/artifact/log/event inspection, approvals, pause/resume/stop/retry/cancel, reconnect, and degraded/offline awareness.

### CLI

The CLI supports human commands and machine/API use, interactive workflows, stable JSON schemas, stable exit codes, streaming, CI/non-interactive operation, profiles, authentication, local/remote control, session/execution attachment, Unix pipelines, and machine-readable errors/events.

All interfaces operate against the same SI Core authority.

## Closure rules

Every phase must include implementation, unit/integration tests, security/adversarial tests, edge/failure tests, documentation, current/index synchronization, and final CI. After every phase, update `README.md`, `docs/README.md`, `docs/architecture/README.md`, this plan, `docs/architecture/PHASES.md`, the relevant phase record, and affected cross-cutting documentation. Historical phase records preserve phase-time evidence; current/index documents must reflect the latest verified status. Before completion, perform a stale-status/documentation audit and verify final exact-tree mainline CI. If CI fails, inspect diagnostics/artifacts, fix the root cause, rerun, and only then continue.
