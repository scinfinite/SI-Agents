# V4 Phases

43. Final v3 Integration & Hardening — historical V3 close

## Status legend

- **Complete** — implementation, tests, documentation, and final CI evidence verified.
- **Advanced hardened** — a closed phase was re-audited with additional production/security invariants and green hardening CI; final mainline exact-tree CI is the closure gate.
- **In implementation** — active phase implementation/tests/docs are in progress; final mainline exact-tree CI is still required.
- **Next** — planned next implementation phase.
- **Planned** — future roadmap phase.

## V4 sequence and current status

| Phase | Name | Status | Evidence |
|---:|---|---|---|
| 44 | Execution Runtime Foundation | Complete | CI #919 / `34610448789` |
| 45 | Event Bus + State Architecture | Complete | CI #935 / `34612616978` |
| 46 | Parallel Scheduler + Executor | **Advanced hardened** | Hardening CI #984 / `34671292491` |
| 47 | OpenCode Bridge | **Advanced hardened** | Hardening CI #984 / `34671292491` |
| 48 | OmniRoute Integration | Complete | CI #949 / `34623762921` |
| 49 | Agent + Team Builder | **Advanced hardened** | Hardening CI #984 / `34671292491` |
| 50 | Capability Authorization | **Advanced hardened** | Hardening CI #984 / `34671292491` |
| 51 | Checkpoints + Resume | Complete | CI #977 / `34627956634` |
| 52 | Context / Memory Economics | **In implementation** | Active branch implementation + adversarial tests + architecture docs; final mainline CI pending |
| 53 | Persistent Sessions | Planned | Planned |
| 54 | Human-in-the-Loop | Planned | Planned |
| 55 | Durable Waiting + Scheduling | Planned | Planned |
| 56 | Intelligent Routing + Economics | Planned | Planned |
| 57 | Security Platform | Planned | Planned |
| 58 | Workspace / Worktree Lifecycle | Planned | Planned |
| 59 | Observability | Planned | Planned |
| 60 | Evaluation + Benchmarking | Planned | Planned |
| 61 | Continuous Improvement | Planned | Planned |
| 62 | Cross-Runtime / Cross-Harness | Planned | Planned |
| 63 | Ecosystem / Marketplace | Planned | Planned |
| 64 | SDK / Developer Platform | Planned | Planned |
| 65 | Workflow + Automation | Planned | Planned |
| 66 | Advanced Web Control Plane | Planned | Planned |
| 67 | Advanced TUI Control Center | Planned | Planned |
| 68 | Advanced CLI Platform | Planned | Planned |
| 69 | npm Distribution + Setup | Planned | Planned |
| 70 | End-to-End Production Validation | Planned | Planned |
| 71 | Final Production Hardening | Planned | Planned |

## Advanced hardening audit

### Phase 46 — Parallel Scheduler + Executor

Scheduler-bound explicit execution identity checks, idempotent matching resubmissions, conflict-safe rejection, dependency graph cycle defense, bounded parallelism, durable recovery, cancellation finalization, dependency propagation, EventBus integration, and runtime-authoritative state.

### Phase 47 — OpenCode Bridge

Per-request timeout propagation, bounded 1 MiB SSE frames, strict terminal stream semantics, session filtering, cancellation/abort, error normalization, loopback-default endpoint security, metadata allowlisting, and SI/OpenCode authority separation.

### Phase 49 — Agent + Team Builder

Schema-versioned deterministic catalogs/manifests, stronger duplicate definition/metadata validation, explicit capability/model/resource declarations, acyclic handoffs, deterministic topological execution layers, bounded composition, and declaration/runtime authority separation.

### Phase 50 — Capability Authorization

Request-fingerprint-bound high/critical approvals, approval replay prevention, secret-like metadata rejection, bounded governance inputs, explicit/fail-closed egress, declared-capability enforcement, scope checks, identity binding, and cost/risk controls.

Combined hardening CI **#984 (`34671292491`)** passed distribution, wheel verification, repository audit, integration verification, Ruff, and full pytest. The mainline CI run after merge is the authoritative exact-tree closure gate.

## Detailed planned scope — Phases 52–71

### 52 — Context / Memory Economics

Context budgets; per-user/project/session/workflow/team/task/agent limits; token/cost accounting; context-window awareness; working/shared/persistent memory; execution/artifact/evidence context; relevance/importance scoring; retrieval; targeted injection; compression; summarization; pruning; automatic compaction; deduplication; cross-agent context reuse; snapshots; lineage/provenance; overflow protection; model/cost-aware selection; sensitive-context isolation; secret redaction; permissions; memory quality metrics; auditable deterministic context decisions.

### 53 — Persistent Sessions

Durable session IDs/lifecycle/ownership; history and state; session events/tasks/agents/teams/workflows/models/providers/artifacts/logs/evidence; token/cost history; context/memory; permissions/isolation; recovery; expiration/archival; export/import; cloning/branching; replay; search/filtering; persistent OpenCode relationship; cross-interface continuity across Web/TUI/CLI/OpenCode.

### 54 — Human-in-the-Loop

Approval gates; human input/ask-user tasks; review gates; risk/cost/egress/destructive/security/deployment approvals; agent/team escalation; pause/resume; reject/modify/retry/reassign/alternative route decisions; approval expiration and identity; audit/evidence; notifications; outstanding-approval queues; Web/TUI/CLI controls; fail-closed human decision boundaries.

### 55 — Durable Waiting + Scheduling

Durable WAIT; timers; delayed and recurring execution; cron-like schedules; wake-up events; event-triggered execution; approval/human/dependency/resource/external-event waits; deadlines; timeout scheduling; retry backoff/jitter; restart-safe waits; queue/priority/fairness/starvation controls; scheduling policies; calendar/time execution; long-running workflows without holding workers while waiting.

### 56 — Intelligent Routing + Economics

Task complexity/capability analysis; agent-model/task-model matching; capability/quality/latency/reliability/context-window/streaming/structured-output/vision/coding/reasoning/tool-capability routing; cost-aware routing; preferred/fallback models/providers; health/history signals; model escalation/downgrade; rate-limit/transient failure handling; per-user/project/session/task/agent/team/workflow budgets; cost estimation/forecasting; retry economics; route evidence; circuit breakers/provider recovery; SI orchestration authority with OmniRoute model/provider routing authority.

### 57 — Security Platform

Unified least privilege; identities; scoped permissions/capability tokens; tool/MCP/provider/model/filesystem/command/process/network authorization; secret references/isolation/redaction; workspace and project isolation; egress controls; destructive-operation controls; approval enforcement; audit/security events/evidence; prompt/tool/context injection defenses; agent-to-agent trust boundaries; security/dependency/supply-chain/configuration scanning; adversarial tests; policy versioning; fail-closed defaults.

### 58 — Workspace / Worktree Lifecycle

Workspace creation/destruction; Git worktree/branch lifecycle; per-agent/task/team isolation; explicitly permitted shared workspaces; locking/ownership; dirty-worktree/conflict detection; diff/patch/merge preparation; artifact collection; snapshots/checkpoints; failure/restart cleanup and recovery; authorized workspace resume; permissions/audit history; abandoned-workspace garbage collection.

### 59 — Observability

Live execution/task/agent/team/workflow/model/provider status; queue/running/waiting/approval/retry/checkpoint/failure state; token/cost/latency/throughput/resource metrics; handoffs/dependencies/DAG progress/critical path/bottlenecks; structured logs/metrics/traces; correlation/causation IDs; execution/agent/task/provider/cost/error/evidence timelines; tool/model calls; artifact/diff inspection; search/filter/debug/audit modes; telemetry export; operator health/incident views.

### 60 — Evaluation + Benchmarking

Agent/team/workflow/model/provider/routing/tool evaluations; security/reliability/cost/latency/quality benchmarks; scenarios; golden tasks/outputs; expected behavior; automated/human evaluation; scoring; failure classification; datasets/reports; historical/version comparisons; A/B experiments; regression detection; release gates; evidence-backed results.

### 61 — Continuous Improvement

Failure analysis/clustering; regression detection; performance analysis; optimization recommendations; prompt/skill/agent-definition/routing-policy/workflow improvement proposals; cost/reliability/performance optimization; experiment tracking/versioning; canaries; rollback; human approval for consequential changes; change evidence/history; execute → observe → evaluate → diagnose → improve → test → deploy → observe loop.

### 62 — Cross-Runtime / Cross-Harness

Runtime/session/tool/model/event/capability/context/checkpoint/artifact adapters; common execution/task/agent/event/capability/session/artifact contracts; runtime capability discovery/health; runtime selection/fallback; harness-neutral state; runtime-specific isolation; OpenCode first-class integration without making SI Core OpenCode-dependent.

### 63 — Ecosystem / Marketplace

Governed agent/skill/tool/team/workflow/model-profile/provider-profile/MCP/extension packages; manifests; versioning; dependencies; compatibility; capability/permission declarations; security scanning; provenance; signatures/trust where supported; install/update/uninstall/rollback; drift detection; local/private registries; official/community registry; templates; governance gates preventing silent authorization bypass.

### 64 — SDK / Developer Platform

Python and TypeScript/JavaScript SDKs; versioned REST; WebSocket/SSE; control/execution/task/agent/team/workflow/session/event/artifact/approval/evaluation/observability APIs; typed schemas; stable errors; authentication/authorization; idempotency; concurrency controls; pagination/filtering; webhooks; event subscriptions; CI/CD integration; examples and developer documentation/tooling.

### 65 — Workflow + Automation

Sequential/parallel/conditional/looping/fan-out/fan-in/dynamic DAGs; agent/team delegation; human gates; durable waits; timers; schedules; webhooks; event triggers; retry policies; failure branches; compensation; rollback; checkpoints/resume; workflow versioning/templates; import/export; visualization; Git/GitHub, CI/CD, issue tracker, chat, API, webhook, MCP, filesystem and developer-tool integrations.

### 66 — Advanced Web Control Plane

Localhost-first richest interface; live dashboard; active/queued/waiting/failed executions; live agent/team/task activity; model/provider/route health; cost/token/resource views; interactive execution DAG/workflow canvas; timelines/live events; dependency visualization; logs/evidence/artifacts; code/Markdown/JSON/diff viewers; artifact previews; search/global navigation; command palette; keyboard shortcuts; contextual actions; authorized start/stop/pause/resume/retry/cancel/approve/reject/reassign/inspect/replay/checkpoint-resume; dark/light themes; responsive desktop/tablet/mobile; accessibility; skeleton/empty/error states; meaningful status animation/transitions; control of work started from CLI/TUI/OpenCode through shared SI Core.

### 67 — Advanced TUI Control Center

Terminal-native operator cockpit; dashboard/executions/tasks/agents/teams/workflows/models/providers/approvals/events/logs/evidence/artifacts/automation/system; live refresh/streaming; split panes; trees; DAG/progress/timelines; fuzzy search; filtering/sorting; keyboard navigation; JSON/diff/artifact/log/event inspection; approvals; pause/resume/stop/retry/cancel/reconnect; offline/degraded/reconnect-aware operation; terminal-native notifications; same authoritative state/control API as Web/CLI.

### 68 — Advanced CLI Platform

Human commands for run/task/agent/team/workflow/session/execution/approval/resume/logs/events/models/providers/status; interactive selection/completion; context-aware commands; profiles/config/auth; local/remote control; session/execution attachment; live streaming; JSON schemas; stable exit codes; CI/non-interactive mode; quiet/verbose/debug; Unix pipelines; machine-readable events/errors; SI Core remains the business authority.

### 69 — npm Distribution + Setup

npm package/global CLI; one-command installation; first-run startup; platform/architecture detection; Linux/macOS/Windows/ARM/x64 support where dependencies permit; bootstrap; setup wizard; OpenCode and OmniRoute detection/configuration; SI Core setup/validation; local Web/TUI/CLI availability; health checks; diagnostics; upgrade/uninstall; version/migration handling; clean-machine validation. Target experience: install SI-Agents → connect/configure OpenCode and OmniRoute → start SI → use Web/TUI/CLI/OpenCode without manually assembling internal components.

### 70 — End-to-End Production Validation

Real OpenCode → SI → OmniRoute → model/provider → SI → OpenCode flow; single/multiple/parallel agents; teams; handoffs; dependencies; reviews; fallback; rate limits; timeouts; retries; circuit breakers; cancellation; pause/resume; checkpoints; durable waits; approvals; restart recovery; session/workspace recovery; authorization and injection attacks; secret leakage attempts; context/cost limits; long/large workflows; Web/TUI/CLI control of the same executions; installation/upgrade/clean setup; cross-runtime scenarios; artifacts/evidence/telemetry/evaluation.

### 71 — Final Production Hardening

Final architecture/authority/state-machine audit; concurrency/race/idempotency/stale-state audit; persistence/crash/restart/partial-execution audit; authorization/secrets/egress/tool/supply-chain audit; OpenCode/OmniRoute/runtime/provider failure audit; context/memory/economics; scheduler/workflow; workspace; observability/evidence; Web/TUI/CLI UX/accessibility/reconnect/degraded modes; SDK/API compatibility/schema stability; npm packaging/install/upgrade/migration. Validate duplicate requests/events, concurrent conflicts, lost connections, provider/runtime failures, persistence failures, authorization replay/privilege escalation, secret/metadata injection, prompt/tool/context injection, resource exhaustion, performance/load, and full end-to-end scenarios. Release evidence must include repository audit, package/wheel verification, integration, Ruff, compileall, full pytest, security/adversarial, E2E, performance/reliability, installation/upgrade, exact-tree, documentation, and final mainline CI.

## V4 integration markers

- **OpenCode ↔ SI:** OpenCode is a primary user-facing harness; the SI bridge adapts transport/session behavior while SI Core owns execution authority.
- **SI ↔ OmniRoute:** OmniRoute provides model/provider/API routing; SI owns task decomposition, agent/team orchestration, governance, budgets, evidence, and execution lifecycle.
- **Parallel agents:** scheduler + team topology support multiple concurrent agents with bounded resources and explicit dependencies/handoffs.
- **Web/TUI/CLI:** all are first-class control surfaces over the same authoritative SI Core state.
- **Installation:** Phase 69 targets a one-command npm installation and simple OpenCode/OmniRoute configuration.
- **Circuit/fallback behavior:** routing and scheduler layers must stop, retry, or switch according to explicit policy, budgets, provider health, and authorization rather than implicit uncontrolled fallback.

## Closure rule

Do not mark a phase or hardening audit complete until implementation and tests pass repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, and the final exact-tree CI. After every phase and cross-phase hardening audit, update `README.md`, `docs/README.md`, `docs/architecture/README.md`, `docs/architecture/SI_AGENTS_V4_PLAN.md`, this phase index, the relevant phase record, and affected cross-cutting documentation. Historical phase records preserve phase-time evidence; current/index documents must reflect the latest verified status.
