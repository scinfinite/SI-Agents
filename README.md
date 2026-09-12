# SI-Agents

SI-Agents is the governed execution and agent platform for Project-SI. V4 is being built as one authoritative SI Core exposed through Web, TUI, CLI, OpenCode, and runtime/integration adapters.

## V4 product direction

```text
User prompt → OpenCode → SI Core → Scheduler/Orchestrator
→ Agents/Teams/Workflows → Authorization → OmniRoute
→ Models/Providers/APIs → Results/Evidence → SI Core
→ OpenCode / Web / TUI / CLI
```

OpenCode is a primary user-facing harness. OmniRoute is the model/provider/API routing layer. SI Core remains authoritative for execution state, orchestration, governance, evidence, lifecycle, persistence, and recovery.

## Current V4 status

- **Phases 44–60 are complete on main.**
- **Phase 61 — Continuous Improvement is next.**
- **Phases 46, 47, 49, and 50 have additionally passed advanced-level hardening.**
- Phase 54 final synchronized-tree mainline CI **#1051 (`34676632475`)** passed distribution, wheel verification, repository audit, integration verification, Ruff, and full pytest.
- Phase 55 final synchronized-tree closure CI **#1080 (`34678317246`)** passed all required repository gates.
- Phase 56 final synchronized-tree mainline CI **#1095 (`34682748193`)** passed all required repository gates on the synchronized Phase 56 tree.

## Phase 56 — Intelligent Routing + Economics

Phase 56 adds deterministic SI-side routing intelligence while preserving OmniRoute as the model/provider/API routing boundary.

Covered contracts:

- explicit task complexity and capability requirements;
- model/agent capability, context-window, streaming, structured-output, vision, coding, reasoning, and tool matching;
- quality, reliability-history, latency, cost, and preference scoring;
- quota, provider/model enablement, and circuit-breaker gating;
- preferred providers/models and deterministic tie-breaking;
- budget reservations and settlement with fail-closed limits;
- cost and retry forecasting;
- bounded transient/rate-limit fallback;
- escalation/downgrade controls;
- non-secret route evidence and failure classification;
- health outcome recording and recovery probes.

The implementation lives in `core/provider_intelligence/intelligent_router.py`, with adversarial/unit coverage in `tests/test_phase56_intelligent_routing.py`.

## Phase 55 — Durable Waiting + Scheduling

Phase 55 adds durable SQLite-backed SI Core waiting and scheduling with an explicit `waiting → ready → claimed → completed` lifecycle.

Covered contracts:

- timer and delayed waits without occupying execution workers;
- recurring interval schedules with bounded occurrence counts;
- validated five-field UTC cron schedules;
- approval, human, dependency, resource, and external wake conditions;
- deadlines and fail-closed expiry;
- restart-safe state and ordered lifecycle events;
- priority plus bounded age-based starvation resistance;
- optimistic revisions and concurrency-safe claiming/completion;
- bounded queue and payload sizes;
- secret-like payload rejection and JSON-safe state;
- identity/project isolation;
- Control API create/list/get/events/wake/claim/complete/cancel routes.

A wait is scheduling state, not an authorization grant. Claims never restore or grant credentials, capabilities, provider authorization, or identity; downstream execution must authorize independently.

## Advanced-hardened phases

### Phase 46 — Parallel Scheduler + Executor

Advanced hardening covers explicit execution identity conflicts, scheduler/runtime idempotency, dependency graph cycle defense, bounded concurrency, durable recovery, cancellation finalization, dependency failure propagation, EventBus integration, and authority boundaries.

### Phase 47 — OpenCode Bridge

Advanced hardening covers per-request transport timeout propagation, bounded 1 MiB SSE frames, strict terminal events, session filtering, cancellation, error normalization, loopback-default endpoint security, and the SI/OpenCode authority boundary.

### Phase 49 — Agent + Team Builder

Advanced hardening covers schema-versioned deterministic catalogs/manifests, stronger definition and metadata validation, acyclic handoff graphs, deterministic execution layers, bounded team composition, capability declarations, and separation of declarations from runtime authority.

### Phase 50 — Capability Authorization

Advanced hardening covers request-fingerprint-bound high/critical approvals, approval replay prevention, secret-like metadata rejection, bounded governance inputs, explicit/fail-closed egress semantics, declared-capability enforcement, scope checks, cost/risk controls, and deterministic evidence.

## V4 roadmap — detailed scope

The full detailed roadmap is maintained in `docs/architecture/SI_AGENTS_V4_PLAN.md`.

| Phase | Name | Scope focus |
|---:|---|---|
| 44 | Execution Runtime Foundation | Durable execution, attempts, lifecycle, cancellation, recovery |
| 45 | Event Bus + State Architecture | Durable events, ordering, replay, projections |
| 46 | Parallel Scheduler + Executor | DAGs, bounded parallelism, fan-out/fan-in, recovery |
| 47 | OpenCode Bridge | Sessions, message/prompt transport, SSE, cancellation |
| 48 | OmniRoute Integration | Models/providers, routing, streaming, fallbacks |
| 49 | Agent + Team Builder | Agent/team definitions, handoffs, deterministic topology |
| 50 | Capability Authorization | Scoped grants, risk, approvals, egress, fail-closed policy |
| 51 | Checkpoints + Resume | Durable checkpoints, lineage, integrity, safe resume |
| 52 | Context / Memory Economics | Context budgets, memory, compaction, relevance, token/cost economics |
| 53 | Persistent Sessions | Durable sessions, history, memory, replay, export/import, branching, cross-interface continuity |
| 54 | Human-in-the-Loop | Approvals, human input, review/escalation, controlled resume |
| 55 | Durable Waiting + Scheduling | Durable waits, timers, schedules, triggers, long-running work |
| 56 | Intelligent Routing + Economics | Capability/quality/cost/latency routing and provider economics |
| 57 | Security Platform | Least privilege, secrets, tools/MCP, egress, injection defense, audit |
| 58 | Workspace / Worktree Lifecycle | Isolated workspaces, Git worktrees, branches, diffs, cleanup/recovery |
| 59 | Observability | Live status, logs, metrics, traces, timelines, evidence |
| 60 | Evaluation + Benchmarking | Golden tasks, benchmarks, scoring, regression and A/B evaluation |
| 61 | Continuous Improvement | Failure analysis, optimization, experiments, rollback, improvement loop |
| 62 | Cross-Runtime / Cross-Harness | Common contracts and adapters beyond one runtime/harness |
| 63 | Ecosystem / Marketplace | Governed agents, skills, tools, teams, workflows, integrations |
| 64 | SDK / Developer Platform | Python/TypeScript SDKs, REST, streaming, webhooks, stable schemas |
| 65 | Workflow + Automation | Durable DAG automation, triggers, branches, compensation, integrations |
| 66 | Advanced Web Control Plane | Full localhost operational control, DAG, live status, artifacts, approvals |
| 67 | Advanced TUI Control Center | Terminal-native live operator cockpit and control |
| 68 | Advanced CLI Platform | Human + machine CLI, JSON, exit codes, streaming, CI automation |
| 69 | npm Distribution + Setup | One-command installation, setup, OpenCode/OmniRoute configuration |
| 70 | End-to-End Production Validation | Full real-user path, failure/recovery/security/UI/install scenarios |
| 71 | Final Production Hardening | Final architecture, security, reliability, UX, packaging and release gate |

## V4 interface contract

- **Web:** localhost-first and richest control plane; live executions, agents, tasks, teams, workflows, DAGs, logs, events, artifacts, diffs, routing, cost, approvals, health, search, command palette, responsive/accessibility support.
- **TUI:** terminal-native operator cockpit with live refresh/streams, split panes, trees, DAG/progress views, search/filtering, inspection, approvals, pause/resume/stop/retry/cancel/reconnect.
- **CLI:** stable human and machine interface with normal commands, JSON schemas, exit codes, streaming, CI/non-interactive operation, profiles, and scripting.
- **Shared authority:** all surfaces inspect/control the same SI Core state; none creates a competing business authority.

## Engineering gate

A phase is not complete until implementation, security/adversarial tests, edge/failure tests, documentation synchronization, repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, and the final exact-tree CI run are green. After every phase and cross-phase hardening audit, README, docs/index, architecture/index, V4 plan, phase index, phase records, and affected cross-cutting documents must be synchronized.
