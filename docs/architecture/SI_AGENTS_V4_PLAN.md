# SI-Agents V4 Plan

## V4 product vision

SI-Agents V4 is planned as a production-grade, governed, persistent, observable, multi-agent orchestration platform built around **one authoritative SI Core**.

The intended primary flow is:

```text
User prompt
  ↓
OpenCode
  ↓
SI OpenCode Bridge
  ↓
SI Core / Control API
  ↓
Scheduler + Orchestrator
  ↓
Tasks / Agents / Teams / Workflows
  ↓
Capability Authorization
  ↓
OmniRoute
  ↓
Models / Providers / APIs
  ↓
Results / Artifacts / Evidence
  ↓
SI Core
  ↓
OpenCode / Web / TUI / CLI
```

**Authority boundary:** OpenCode is a primary user-facing coding harness; OmniRoute is the model/provider/API routing layer; SI Core owns execution state, orchestration, governance, evidence, lifecycle, and recovery. External runtimes and providers are adapters and never become authoritative state owners.

## Current verified position

V3 is closed. V4 implementation has completed Phases 44–51 in sequence. Phases 46, 47, 49, and 50 subsequently passed an advanced-level hardening audit without reopening the phase sequence. Phase 52 is the next implementation phase.

### Advanced hardening position

Combined advanced audit CI **#984 (`34671292491`)** passed distribution, wheel verification, repository audit, integration verification, Ruff, and the complete pytest suite. The corresponding changes were merged to `main`; the post-merge mainline CI is the authoritative exact-tree closure gate.

### Phase 44 — Execution Runtime Foundation

Complete. The authoritative runtime provides durable execution and attempt identity, canonical lifecycle transitions, idempotency, cancellation, pause/resume boundaries, deadlines, retry/new-attempt semantics, restart recovery, adapter isolation, terminality protection, and secret isolation.

Evidence: CI #919 / `34610448789`.

### Phase 45 — Event Bus + State Architecture

Complete. The durable append-only EventBus provides stable event identity, per-aggregate ordering, correlation/causation metadata, idempotent publication, replay, live subscriptions, durable projections/checkpoints, and event counts. Runtime state remains authoritative; events are the durable integration history.

Evidence: CI #935 / `34612616978`.

### Phase 46 — Parallel Scheduler + Executor — advanced hardened

Advanced hardening covers durable dependency-aware DAG scheduling; bounded parallel workers, fan-out/fan-in, priority and aging; queued/running cancellation and dependency failure propagation; restart recovery and EventBus integration; scheduler-bound explicit execution identity checks; idempotent resubmission when orchestration metadata matches; conflict rejection without mutating an existing schedule; dependency graph/cycle defense; runtime-authoritative finalization and cancellation; and security/authority boundary protection.

Evidence: hardening CI #984 / `34671292491`.

### Phase 47 — OpenCode Bridge — advanced hardened

Advanced hardening covers health discovery and session creation/reuse; blocking message invocation and asynchronous prompt/SSE streaming; per-request timeout propagation to HTTP/SSE transport; bounded 1 MiB SSE frame buffering; strict terminal-event streaming semantics; cancellation/abort support; session-filtered event normalization; request/session correlation; terminal/error normalization without upstream-body leakage; whitelisted request metadata forwarding; loopback-only default endpoint security with explicit remote opt-in; and SI Core authority.

Evidence: hardening CI #984 / `34671292491`.

### Phase 48 — OmniRoute Integration

Complete. The bridge supports health/model discovery, capability-aware route selection, preferred/fallback candidates, OpenAI-compatible chat completions, streaming/non-streaming responses, usage normalization, upstream error classification, transient timeout handling, credential references, loopback-default endpoint security, request metadata allowlisting, and explicit authority boundaries.

Evidence: CI #949 / `34623762921`.

### Phase 49 — Agent + Team Builder — advanced hardened

Advanced hardening covers immutable agent definitions and deterministic catalogs; schema-versioned catalogs/manifests; stronger duplicate definition and metadata validation; explicit capability/model/resource declarations; team membership and bounded parallelism; explicit handoffs; acyclic handoff topology; deterministic topological execution layers for parallel composition; deterministic manifests/digests; declaration/runtime authority separation; and no implicit capability granting.

Evidence: hardening CI #984 / `34671292491`.

### Phase 50 — Capability Authorization — advanced hardened

Advanced hardening covers explicit scoped grants and deny precedence; declared-capability enforcement; subject identity binding; fail-closed conditions and defaults; request-fingerprint-bound high/critical approvals; approval replay prevention when authorization inputs change; secret-like governance metadata rejection before evidence creation; bounded governance input sizes; explicit external-egress policy and fail-closed semantics; cost limits and risk controls; and deterministic non-secret authorization evidence.

Evidence: hardening CI #984 / `34671292491`.

### Phase 51 — Checkpoints + Resume

Complete. `CheckpointStore`, `Checkpoint`, `ResumePlan`, and `CheckpointError` provide append-only SQLite checkpoint persistence, ordered lineage, SHA-256 integrity, parent validation, secret-like field rejection, bounded serialized state/metadata, durable reopen, terminal-only resume through `ExecutionStore.new_attempt()`, and optional EventBus facts. Checkpoints preserve progress evidence but never restore authority, credentials, capabilities, grants, provider authorization, or identity.

Evidence: CI #977 / `34627956634`.

---

# Detailed V4 roadmap — Phases 52–71

The following is the detailed product specification represented by the phase sequence. Feature lists are planning scope, not claims of implementation. A phase becomes complete only after implementation, tests, security/adversarial coverage, documentation synchronization, and final CI verification.

## Phase 52 — Context / Memory Economics

Build an intelligent context and memory layer that controls token use, relevance, cost, privacy, and context-window pressure across long-running multi-agent work.

### Planned capabilities

- Context manager and context budgets.
- Per-user, project, session, workflow, team, task, and agent context budgets.
- Token/cost accounting and context-window awareness.
- Working memory, shared team memory, persistent memory, execution context, artifact context, and evidence context.
- Context prioritization, relevance scoring, and importance scoring.
- Memory expiration/TTL.
- Context retrieval and targeted context injection.
- Context compression, summarization, pruning, and automatic compaction.
- Context deduplication and reuse between agents.
- Avoid duplicate context transmission across parallel agents.
- Context snapshots and lineage/provenance.
- Context overflow protection.
- Model-aware and cost-aware context selection.
- Sensitive-context isolation and secret redaction.
- Context access permissions.
- Memory quality and utilization metrics.
- Deterministic context decisions with auditable evidence.

## Phase 53 — Persistent Sessions

Turn executions into durable user sessions that can span many tasks, agents, models, workflows, and restarts.

### Planned capabilities

- Session IDs, lifecycle, ownership, metadata, history, and authoritative state.
- Session events, tasks, agents, teams, workflows, models, providers, artifacts, logs, evidence, token usage, and cost history.
- Session context and memory.
- Session permissions and isolation.
- Session recovery and restart/resume.
- Session expiration and archival.
- Session export/import.
- Session cloning and branching.
- Session replay and inspection.
- Session search and filtering.
- Persistent OpenCode relationship.
- Cross-interface session continuity so CLI, TUI, Web, and OpenCode can inspect/control the same authoritative session.

## Phase 54 — Human-in-the-Loop

Make human participation a first-class execution state rather than an out-of-band workaround.

### Planned capabilities

- Approval requests and approval gates.
- Human input/ask-user tasks.
- Review gates and risk-based approvals.
- Cost, external-egress, destructive-operation, security, and deployment approvals.
- Agent/team escalation.
- Pause for human and resume after human response.
- Reject, modify, retry, reassign, or choose an alternative agent/model/provider where policy permits.
- Approval expiration and identity binding.
- Approval audit trail and evidence.
- Web, TUI, and CLI approval/control surfaces.
- Notifications and outstanding-approval queues.
- Fail-closed behavior when required human decisions are absent or invalid.

## Phase 55 — Durable Waiting + Scheduling

Extend the scheduler into a durable workflow waiting/scheduling system capable of safely holding long-running work without consuming execution workers.

### Planned capabilities

- Durable WAIT state.
- Timers and delayed execution.
- Scheduled and recurring tasks.
- Cron-like schedules.
- Wake-up events and event-triggered execution.
- Approval, human-response, dependency, resource, and external-event waits.
- Deadline and timeout scheduling.
- Retry scheduling with backoff and jitter.
- Restart-safe waits and resume.
- Queue, priority, fairness, and starvation prevention.
- Scheduling policies and calendar/time-based execution.
- Long-running workflow support.

## Phase 56 — Intelligent Routing + Economics

Make orchestration and model selection economically and operationally intelligent while keeping OmniRoute as the model/provider routing layer.

### Planned capabilities

- Task complexity and capability analysis.
- Agent-model and task-model matching.
- Capability, quality, latency, reliability, context-window, streaming, structured-output, vision, coding, reasoning, and tool-capability routing.
- Cost-aware, latency-aware, quality-aware, and reliability-aware routing.
- Preferred/fallback models and providers.
- Provider health and historical success signals.
- Automatic model escalation and downgrade.
- Rate-limit and transient-failure handling.
- Per-user/project/session/task/agent/team/workflow budgets.
- Pre-execution cost estimation and forecasting.
- Retry economics and route-decision evidence.
- Circuit breakers and provider recovery.
- SI decides work decomposition and orchestration; OmniRoute selects model/provider/API routes.

## Phase 57 — Security Platform

Unify security controls across execution, tools, agents, teams, sessions, workspaces, network egress, providers, and integrations.

### Planned capabilities

- Capability-based security and least privilege.
- User, agent, team, session, execution, and workspace identities.
- Scoped permissions and capability tokens.
- Tool, MCP, provider, model, filesystem, command, process, and network authorization.
- Secret references, isolation, redaction, and non-leakage.
- Workspace and tenant/project isolation.
- Network-egress controls.
- Destructive-operation controls.
- Approval enforcement.
- Audit/security events and evidence.
- Prompt-injection, tool-injection, and context-poisoning defenses.
- Agent-to-agent trust boundaries.
- Security scanning, dependency/supply-chain checks, configuration security, and adversarial policy tests.
- Security policy versioning and fail-closed defaults.

## Phase 58 — Workspace / Worktree Lifecycle

Give agents safe, durable and auditable development workspaces and Git worktrees.

### Planned capabilities

- Workspace creation/destruction.
- Git worktree and branch lifecycle.
- Per-agent, per-task, and per-team isolation.
- Shared workspaces where explicitly permitted.
- Workspace locking and ownership.
- Dirty-worktree and conflict detection.
- Diff/patch generation and review.
- Merge preparation.
- Artifact collection.
- Workspace snapshots/checkpoints.
- Failure/restart cleanup and recovery.
- Resume into the prior authorized workspace.
- Workspace permissions and audit history.
- Automatic garbage collection of abandoned workspaces.

## Phase 59 — Observability

Make every important execution decision and state transition inspectable in Web, TUI, CLI, logs, events, metrics, and traces.

### Planned capabilities

- Live execution/task/agent/team/workflow/provider/model status.
- Queue, running, waiting, approval, retry, checkpoint, and failure states.
- Token, cost, latency, throughput, and resource metrics.
- Agent handoffs, task dependencies, DAG progress, critical path, and bottlenecks.
- Structured logs, metrics, traces, correlation IDs, and causation IDs.
- Execution, agent, task, provider, cost, error, and evidence timelines.
- Tool/model call visibility.
- Artifact and diff inspection.
- Search/filter/debug/audit modes.
- Exportable telemetry.
- Operator-oriented health and incident views.

## Phase 60 — Evaluation + Benchmarking

Create a rigorous evaluation system so agent, team, workflow, routing, security, reliability, cost, and quality changes are measurable.

### Planned capabilities

- Agent, team, workflow, model, provider, routing, and tool-use evaluations.
- Security, reliability, cost, latency, and quality benchmarks.
- Scenario tests, golden tasks, expected behavior, and golden outputs.
- Automated and human evaluation.
- Quality/success scoring and failure classification.
- Evaluation datasets and reports.
- Historical and version comparisons.
- Agent/model/routing A/B experiments.
- Regression detection and release gates.
- Evidence-backed evaluation results.

## Phase 61 — Continuous Improvement

Turn execution and evaluation data into a controlled improvement loop.

### Planned capabilities

- Failure analysis and failure clustering.
- Regression detection.
- Agent/team/model/routing/workflow performance analysis.
- Automatic optimization recommendations.
- Prompt, skill, agent-definition, routing-policy, and workflow improvement proposals.
- Cost, reliability, and performance optimization.
- Experiment tracking and versioning.
- Canary changes and rollback.
- Human approval for consequential changes.
- Change evidence and improvement history.
- Closed loop: execute → observe → evaluate → diagnose → improve → test → deploy → observe.

## Phase 62 — Cross-Runtime / Cross-Harness

Keep SI orchestration portable across OpenCode and future agent runtimes/harnesses through explicit adapters and common contracts.

### Planned capabilities

- Runtime, session, tool, model, event, capability, context, checkpoint, and artifact adapters.
- Common execution, task, agent, event, capability, session, and artifact contracts.
- Runtime capability discovery and health.
- Runtime selection and fallback.
- Harness-neutral execution state.
- Runtime-specific isolation without changing SI authority.
- OpenCode as a first-class integration without making the core architecture OpenCode-dependent.

## Phase 63 — Ecosystem / Marketplace

Provide a governed ecosystem for agents, skills, tools, teams, workflows, model profiles, provider profiles, MCP integrations, and extensions.

### Planned capabilities

- Package manifests and versioning.
- Dependency resolution and compatibility checks.
- Capability and permission declarations.
- Security scanning and provenance.
- Package signatures/trust levels where supported.
- Install, update, uninstall, rollback, and drift detection.
- Local/private registries.
- Official/community registry model.
- Agent, skill, team, workflow, integration, and tool templates.
- Governance gates so extensions cannot silently bypass SI authorization.

## Phase 64 — SDK / Developer Platform

Expose SI as a stable programmable orchestration platform.

### Planned capabilities

- Python SDK.
- TypeScript/JavaScript SDK.
- Versioned REST API.
- WebSocket/SSE streaming API.
- Control, execution, task, agent, team, workflow, session, event, artifact, approval, evaluation, and observability APIs.
- Typed schemas and stable error contracts.
- Authentication and authorization.
- Idempotency and concurrency controls.
- Pagination/filtering.
- Webhooks and event subscriptions.
- CI/CD integration.
- Examples, reference documentation, and developer tooling.

## Phase 65 — Workflow + Automation

Build a durable, visualizable automation layer on top of the runtime, scheduler, agents, teams, events, waits, and approvals.

### Planned capabilities

- Sequential, parallel, conditional, looping, fan-out/fan-in, and dynamic DAG workflows.
- Agent and team delegation.
- Human gates and durable waits.
- Timers, schedules, webhooks, and event triggers.
- Retry policies, failure branches, compensation, and rollback.
- Checkpoints and resume.
- Workflow versioning and templates.
- Import/export.
- Workflow visualization.
- Git/GitHub, CI/CD, issue trackers, chat, APIs, webhooks, MCP, filesystem, and developer-tool integrations.

## Phase 66 — Advanced Web Control Plane

Make localhost Web the richest SI interface and a complete operational control plane, not a passive dashboard.

### Planned capabilities

- Live system dashboard.
- Active/queued/waiting/failed executions.
- Live agent/team/task activity.
- Model/provider/route health.
- Cost/token/resource views.
- Interactive execution DAG and workflow canvas.
- Execution timelines and live event streams.
- Agent/task dependency visualization.
- Logs, evidence, artifacts, code, Markdown, JSON, and diff viewers.
- Artifact previews.
- Search and global navigation.
- Command palette and keyboard shortcuts.
- Contextual actions.
- Start, stop, pause, resume, retry, cancel, approve, reject, reassign, inspect, replay, and checkpoint-resume controls subject to authorization.
- Dark/light themes.
- Responsive desktop/tablet/mobile layouts.
- Accessibility.
- Skeleton loading, empty/error states, confirmations, and meaningful status animations/transitions.
- Animation is for communicating state, progress, change, and feedback rather than decoration.
- Web can inspect/control work started from CLI, TUI, or OpenCode because all surfaces share SI Core authority.

## Phase 67 — Advanced TUI Control Center

Make TUI a terminal-native operator cockpit with full live operational control.

### Planned capabilities

- Dashboard, executions, tasks, agents, teams, workflows, models, providers, approvals, events, logs, evidence, artifacts, automation, and system views.
- Live refresh and streaming.
- Split panes, trees, DAG-oriented views, and progress/timeline displays.
- Fuzzy search, filters, sorting, and keyboard navigation.
- JSON, diff, artifact, log, and event inspection.
- Approval controls.
- Pause, resume, stop, retry, cancel, reconnect.
- Offline/degraded/reconnect-aware operation.
- Terminal-native notifications and status indicators.
- Same authoritative state and control API as Web/CLI.

## Phase 68 — Advanced CLI Platform

Provide a stable CLI for interactive humans, shell automation, CI/CD, and machine consumers.

### Planned capabilities

- Human-oriented commands for run/task/agent/team/workflow/session/execution/approval/resume/logs/events/models/providers/status.
- Interactive command selection and completion.
- Context-aware commands.
- Profiles, configuration, authentication, local/remote control.
- Session/execution attachment and live streaming.
- JSON output with stable schemas.
- Stable exit codes.
- Non-interactive CI mode.
- Quiet/verbose/debug modes.
- Unix-friendly pipelines.
- Machine-readable event/error output.
- CLI operations remain clients of SI Core rather than a second business authority.

## Phase 69 — npm Distribution + Setup

Make installation and first-run configuration as simple as modern developer tools such as OpenCode and OmniRoute.

### Planned capabilities

- npm package and globally installable CLI distribution.
- One-command installation and simple first-run startup.
- Platform/architecture detection.
- Linux, macOS, Windows, ARM, and x64 support where runtime dependencies permit.
- Automatic dependency/bootstrap setup.
- Configuration wizard.
- OpenCode detection/configuration.
- OmniRoute detection/configuration.
- SI Core setup and validation.
- Local Web/TUI/CLI availability after setup.
- Health checks and environment diagnostics.
- Upgrade, uninstall, version/migration handling.
- Clear errors and recovery instructions.
- Clean-machine setup validation.

Target experience: **install SI-Agents → configure/connect OpenCode and OmniRoute → start SI → use Web/TUI/CLI/OpenCode without manually assembling internal components.**

## Phase 70 — End-to-End Production Validation

Validate the entire real-user path rather than relying only on unit/component tests.

### Planned scenarios

- OpenCode prompt through SI to OmniRoute/model/provider and back to OpenCode.
- Single agent, multiple agents, parallel agents, teams, handoffs, dependencies, and reviews.
- Model/provider fallback, rate limits, timeouts, retries, circuit breakers, and failures.
- Cancellation, pause/resume, checkpoint/resume, durable waits, approvals, and restart recovery.
- Persistent session recovery and workspace/worktree recovery.
- Authorization violations, secret leakage attempts, unauthorized tools/egress, prompt/tool/context injection defenses.
- Context and cost limits.
- Long-running and large workflows.
- Web, TUI, and CLI control of the same live executions.
- Installation, upgrade, and clean-environment setup.
- OpenCode and OmniRoute integration.
- Cross-runtime scenarios.
- Artifact, evidence, telemetry, and evaluation verification.

## Phase 71 — Final Production Hardening

The final V4 release gate. This phase is a comprehensive audit and hardening pass rather than a normal feature addition.

### Planned audits

- Architecture and authority boundaries.
- State machines and lifecycle invariants.
- Concurrency, races, idempotency, and stale-state behavior.
- Persistence, crash recovery, restart recovery, and partial execution.
- Authorization, secrets, network egress, tool security, and supply chain.
- OpenCode, OmniRoute, runtime adapters, and provider failure behavior.
- Context/memory and cost economics.
- Scheduler/workflow correctness.
- Workspace/worktree safety.
- Observability and evidence completeness.
- Web/TUI/CLI UX, accessibility, reconnect, and degraded modes.
- SDK/API compatibility and schema stability.
- npm packaging, installation, upgrade, migration, and clean-machine behavior.

### Final reliability/security validation

- Duplicate requests and duplicate events.
- Concurrent updates and conflicting commands.
- Lost network connections and reconnection.
- Provider/model/runtime failures.
- Database and persistence failure scenarios.
- Authorization replay and privilege escalation attempts.
- Secret leakage and metadata injection attempts.
- Prompt/tool/context injection attempts.
- Resource exhaustion and bounded-input behavior.
- Performance and memory/load testing.
- Full end-to-end production scenarios.

### Final release evidence

- Repository audit.
- Distribution/package verification.
- Wheel install/import verification.
- Integration verification.
- Ruff and compileall.
- Full pytest.
- Security/adversarial tests.
- End-to-end tests.
- Performance/reliability tests.
- Installation/upgrade tests.
- Exact-tree verification.
- Documentation verification.
- Final mainline CI green.

---

## V4 surface contract

### Web

Localhost-first and richest interface. It must expose the operational state and controls needed for normal SI work, including live execution, agent/team/task activity, workflow/DAG visualization, approvals, artifacts, logs, evidence, routing, cost, and system health.

### TUI

Terminal-native operator cockpit with live state, inspection, control, approvals, streaming, recovery, and debugging.

### CLI

Human and machine interface with stable commands, JSON schemas, exit codes, streaming, CI/non-interactive operation, and scripting support.

### Shared authority

Web, TUI, CLI, OpenCode, external runtimes, agents, teams, and providers are clients/adapters. They do not maintain competing authoritative business state. SI Core remains authoritative.

## Closure and documentation gate

Every phase and cross-phase hardening audit requires implementation, security/adversarial tests, documentation synchronization, all current/index document updates, and final CI verification. Final CI must cover repository audit, distribution/wheel install/import, integration verification, Ruff, compileall, full pytest, and the final exact-tree state. Historical phase records preserve phase-time evidence; current/index documents must be updated after every phase and hardening audit.
