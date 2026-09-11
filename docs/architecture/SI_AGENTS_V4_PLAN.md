# SI-Agents v4 — Agent Operating System Roadmap

**Status:** Active implementation
**Baseline:** SI-Agents v3, Phases 1–43 complete and CI-verified
**Implemented:** Phases 44–47 complete and final-CI verified
**Current phase:** Phase 48 — OmniRoute Integration
**Planned sequence:** Phases 44–71

> **Planning rule:** This document defines the intended v4 direction and records implementation state where verified. A phase is complete only after implementation, tests, security/adversarial checks, documentation, packaging where relevant, and final CI verification provide evidence.

## 1. Executive vision

SI-Agents v4 evolves the verified v3 governance/control foundation into a real agent operating system: persistent execution, parallel orchestration, durable state/events, live control, first-class OpenCode and OmniRoute integration, richer agents/teams/workflows, security and economics controls, and production-grade Web/TUI/CLI/distribution.

The target experience is:

```text
User / External System
        │
        ├── Web  ───────────────┐
        ├── TUI  ───────────────┤
        ├── CLI  ───────────────┤
        └── OpenCode ───────────┤
                                ▼
                       SI Control API
                       single authority
                                │
                    Workflow / Orchestrator
                                │
                    Runtime / Scheduler
                                │
             ┌──────────────────┼──────────────────┐
             ▼                  ▼                  ▼
        OpenCode            OmniRoute       Native/MCP adapters
             │                  │                  │
             └──────────────────┼──────────────────┘
                                ▼
                         Models / Tools
```

### Product principles

1. **One Core, one authority.** Web, TUI, CLI and integrations use the same SI Core/Control API and authoritative state.
2. **Web-first product surface.** Web is the richest visual control plane and runs locally/localhost-first.
3. **TUI-first operations.** TUI is the fastest terminal-native operator cockpit.
4. **CLI-first automation.** CLI provides stable scripting, JSON output and exit-code contracts.
5. **OpenCode remains the interactive coding harness.** SI integrates with it rather than replacing it.
6. **OmniRoute remains provider/model routing infrastructure.** SI consumes routing capability rather than becoming a competing provider router.
7. **Real parallelism.** Independent tasks execute concurrently within explicit dependency, resource and governance limits.
8. **Persistent observable state.** Every execution is inspectable through correlated events, state, logs, artifacts and evidence.
9. **Explicit control.** Pause, resume, continue, stop, cancellation, retry and approvals are typed state transitions.
10. **Evidence before completion.** Completion requires verification evidence, not an agent assertion alone.
11. **Secure by default.** Secrets stay out of state; capability and authority boundaries fail closed.
12. **Preserve v3 contracts.** Existing governance, personas, skills, memory, organization and Control API capabilities evolve without reopening completed v3 phases.
13. **Surface parity.** Operationally important capabilities are available consistently across Web/TUI/CLI where the surface is appropriate.
14. **Animation communicates state.** Web animation and TUI visual feedback must explain progress/state, never hide or replace authoritative information.
15. **No blind copying.** ECC, Agency Agents, OpenCode, OmniRoute and n8n are reference systems for patterns and research, not implementation dependencies or sources for copied prompts/code.

## 2. V3 → V4 transition

V3 established governance, catalogs, configuration, Control API and operator surfaces. V4 adds durable execution semantics underneath them.

```text
V3: Governance + catalogs + configuration + control surfaces
                         ↓
V4: Runtime + events/state + scheduler + sessions + automation
    + OpenCode/OmniRoute + security/economics + rich Web/TUI/CLI
    + distribution + production validation
```

The implementation order intentionally builds execution/state foundations before final presentation and packaging work.

## 3. Target architecture and contracts

### 3.1 Core domains

- Agent Registry
- Team Registry
- Skill Registry
- Workflow/Runbook Registry
- Task Manager
- Execution Manager
- Scheduler/Executor
- Event Bus
- State Store and projections
- Evidence/Artifact Store
- Governance and authorization
- OpenCode adapter
- OmniRoute adapter
- Automation/scheduling engine
- Session/context/memory services
- Security/secrets platform
- Observability/evaluation services

### 3.2 Canonical identity

Runtime relationships are explicit:

```text
task_id → execution_id → attempt_id
```

Additional stable identifiers include `workflow_id`, `agent_id`, `team_id`, `session_id`, `event_id`, `evidence_id`, `artifact_id`, and `approval_id`.

A retry creates a new attempt under the same execution unless policy explicitly creates a new execution.

### 3.3 Canonical lifecycle

```text
accepted → queued → running → succeeded
                         ├── failed
                         ├── cancelled
                         └── expired
```

Pause/resume, blocked/ready and retry transitions are represented by explicit typed transitions and events. Invalid transitions fail closed.

### 3.4 Authority boundaries

The Control API remains authoritative for caller identity, authorization, admission, policy, authority scope, provenance, approvals, audit and externally visible intent.

The execution runtime owns mechanics only: materializing attempts, invoking adapters, consuming streams/events, enforcing authorized runtime deadlines/cancellation, normalizing outcomes, maintaining runtime state and emitting telemetry/evidence.

Provider routing is downstream. It cannot grant authority, change provenance or bypass governance. OpenCode is a protocol/harness adapter, not a second SI control plane.

## 4. Phase roadmap

## Phase 44 — Execution Runtime Foundation

**Status: Complete + final-CI verified.**

**Objective:** Establish durable execution primitives and the runtime contract.

**Scope:** execution/run model; task model; canonical IDs; lifecycle state machine; attempt model; runtime API contracts; persistence; cancellation; pause/resume; deadlines/timeouts; ownership/cleanup; deterministic transitions; adapter boundary; normalized outcomes; idempotency foundations; restart recovery.

**Acceptance:** executions/tasks have stable IDs; state survives restart; invalid transitions fail; cancellation cleans owned resources; retries create explicit attempts; runtime cannot bypass Control API authority; unit/integration/negative tests cover contracts.

**Final evidence:** CI #919 (`34610448789`) passed distribution, wheel installation/import, repository audit, integration verification, Ruff, compileall and the complete pytest suite.

## Phase 45 — Event Bus + State Architecture

**Status: Complete + final-CI verified.**

**Objective:** Make runtime state durable, ordered, replayable and shared by every surface.

**Scope:** typed append-only event envelope; event/correlation/causation IDs; timestamps and ordering; durable retention; state projections/read models; subscriptions/streaming; replay/reconnect; execution/task/agent/evidence/governance/error/retry events; terminality rules.

**Acceptance:** Web, TUI, CLI and OpenCode observe the same authoritative state; replay reconstructs state; duplicate delivery is safe; exactly one canonical terminal outcome exists per execution/attempt.

**Final evidence:** exact-tree CI #935 (`34612616978`) passed after documentation/evidence alignment.

## Phase 46 — Parallel Scheduler + Executor

**Status: Complete + final-CI verified.**

**Objective:** Execute real task graphs concurrently with deterministic dependency and resource controls.

**Scope:** DAGs; dependency resolution; ready queues; worker pools; bounded concurrency; fan-out/fan-in; retries; deadlines; cancellation propagation; failure recovery; priorities/fairness; resource limits; approval gates; idempotency.

**Acceptance:** independent tasks demonstrably run in parallel; dependencies block correctly; concurrency never exceeds limits; failures follow policy; cancellation propagates safely; scheduler behavior is deterministic under stress tests.

**Final evidence:** CI #938 (`34615157829`) on commit `772716428868a7597540a0bea72f715dfd46a224` passed all repository gates.

## Phase 47 — OpenCode Bridge

**Status: Complete + final-CI verified.**

**Objective:** Connect SI-managed objectives to the current supported OpenCode protocol/session mechanisms.

**Scope:** versioned integration contract; capability discovery/negotiation; session association; task submission; status/progress; event streaming; supported pause/resume/stop/continue operations; result delivery; errors; reconnect/recovery; secure local integration.

**Acceptance:** a user can initiate an SI-managed objective through OpenCode and receive live progress and a verified result without manually synchronizing state. No undocumented coupling is allowed.

**Final evidence:** implementation CI #941 (`34615709124`) passed; final documentation exact-tree CI #942 (`34615862860`) on `main` also passed.

## Phase 48 — OmniRoute Integration

**Status: Next.**

**Objective:** Use OmniRoute as the model/provider access layer without creating a competing router.

**Scope:** health/status; model catalog; capability-aware model policy; preferred/fallback selection; routing adapter; rate-limit/error handling; usage metadata; credential references; interoperability tests.

**Acceptance:** SI can discover usable configured models through OmniRoute and execute the canonical workload through OpenCode → SI → OmniRoute.

## Phase 49 — Agent + Team Builder

**Objective:** Make SI-native agents and teams composable, validated and governable.

**Agent contract:** identity/persona; capabilities; skills; tool permissions; model policy; resource limits; governance; evidence policy; runtime constraints.

**Team contract:** members; roles; routing; parallelism; dependencies; evidence; approvals; failure/retry policy.

**Acceptance:** configurations are typed and validated; UI edits cannot silently grant authority; imported text cannot bypass governance; builder output is deterministic and auditable.

## Phase 50 — Capability Authorization

**Objective:** Turn capabilities, tools and resources into explicit authorization boundaries.

**Scope:** capability registry; allow/deny policy; scoped permissions; resource/action constraints; tool-level authorization; delegation; approval requirements; policy explanations; fail-closed behavior; audit records; secret-aware enforcement.

**Acceptance:** unauthorized actions are rejected before execution; grants are scoped and attributable; policy decisions are observable and testable; no surface can bypass authorization.

## Phase 51 — Checkpoints + Resume

**Objective:** Make long-running execution recoverable without losing provenance.

**Scope:** execution/task checkpoints; durable snapshots; resumable attempts where supported; restart recovery; partial-result handling; checkpoint retention; compatibility/versioning; safe replay; recovery evidence.

**Acceptance:** process/runtime interruption can recover eligible executions deterministically; unsafe/non-resumable work is explicitly marked; resumed work never duplicates an irreversible action without idempotency protection.

## Phase 52 — Context / Memory Economics

**Objective:** Make context and memory useful, bounded and cost-aware.

**Scope:** context budgets; compaction/summarization; retrieval policy; memory tiers; relevance scoring; token/latency/cost accounting; cache policy; context provenance; retention/deletion rules; agent-specific context limits.

**Acceptance:** context growth is bounded; retrieval is attributable; sensitive data follows policy; context/cost metrics are available for evaluation.

## Phase 53 — Persistent Sessions

**Objective:** Provide durable user/agent execution sessions across restarts and surfaces.

**Scope:** session lifecycle; session-to-execution links; resumable conversation/task context; checkpoints; session history; compaction; reconnect; concurrent session safety; retention; export/import where appropriate.

**Acceptance:** users can reconnect to active/recent work from Web/TUI/CLI/OpenCode without creating competing state.

## Phase 54 — Human-in-the-Loop

**Objective:** Make approvals and human decisions first-class execution gates.

**Scope:** approval requests; typed decision payloads; approver identity; scopes; expiry; escalation; deny/cancel behavior; approval UI/CLI/TUI; audit/evidence; sensitive-action confirmation.

**Acceptance:** gated work cannot proceed without required authorization; decisions are durable, attributable and replayable; expired approvals fail safely.

## Phase 55 — Durable Waiting + Scheduling

**Objective:** Support waits, timers, schedules and event-driven continuation without holding workers unnecessarily.

**Scope:** durable timers; cron-like schedules; wait-for-event; queue triggers; delayed retry; wake-up/recovery; time-zone handling; bounded execution windows; cancellation; missed-trigger policy.

**Acceptance:** waiting survives restart; scheduled work is idempotent; worker resources are released during waits; cancellation and expiry are deterministic.

## Phase 56 — Intelligent Routing + Economics

**Objective:** Optimize model/provider choices for capability, reliability, latency and cost while preserving policy.

**Scope:** model capability matrix; workload classification; cost/usage telemetry; latency/reliability scoring; budget policies; fallback strategy; sticky routing where appropriate; quota awareness; cache/compression economics; policy-constrained optimization.

**Acceptance:** routing decisions are explainable and policy-compliant; budget limits cannot be bypassed; economics telemetry supports evaluation.

## Phase 57 — Security Platform

**Objective:** Harden SI as an execution system rather than only a configuration system.

**Scope:** secret isolation; credential references; least privilege; capability sandbox boundaries where supported; input/output trust boundaries; artifact scanning; dependency/security checks; prompt/tool injection defenses; SSRF/network controls; audit integrity; secure defaults; adversarial tests.

**Acceptance:** secrets do not appear in logs/events/artifacts; unauthorized capability use fails closed; security regressions are CI-gated; high-risk operations have explicit policy and audit evidence.

## Phase 58 — Workspace / Worktree Lifecycle

**Objective:** Safely manage isolated workspaces for concurrent agent work.

**Scope:** workspace allocation; Git worktrees/branches where applicable; lifecycle ownership; cleanup; conflict detection; merge/reconciliation workflows; artifact mapping; resource quotas; recovery after interrupted execution.

**Acceptance:** parallel tasks receive explicit workspace ownership; cleanup is reliable; abandoned workspaces are detectable; destructive operations require policy.

## Phase 59 — Observability

**Objective:** Provide production-grade visibility into executions, system health and economics.

**Scope:** structured logs; metrics; traces/correlation; execution timelines; worker health; queue depth; latency; retries; failures; model/provider usage; cost; evidence indexes; diagnostic bundles; retention/redaction.

**Acceptance:** an operator can trace an objective from admission through tasks, adapter calls, events, evidence and final result without exposing secrets.

## Phase 60 — Evaluation + Benchmarking

**Objective:** Measure agent, workflow, runtime and system quality continuously.

**Scope:** deterministic fixtures; benchmark workloads; task success; evidence quality; regression suites; latency/cost/reliability metrics; model comparisons; failure taxonomy; evaluation datasets; release gates.

**Acceptance:** important behavior has repeatable evaluations; regressions are detected before release; benchmark results are attributable to code/config/model changes.

## Phase 61 — Continuous Improvement

**Objective:** Learn from verified execution evidence without allowing silent authority changes.

**Scope:** failure-pattern mining; reusable engineering patterns; recommendations; workflow optimization; agent/skill improvement proposals; evaluation-driven iteration; change provenance; approval for policy-affecting changes; rollback.

**Safety:** learning may recommend or stage changes, but it cannot silently grant permissions, rewrite governance or change authority.

**Acceptance:** every learned improvement has evidence, provenance, evaluation and controlled promotion/rollback.

## Phase 62 — Cross-Runtime / Cross-Harness

**Objective:** Make SI portable across supported execution harnesses and runtimes through adapters.

**Scope:** adapter SDK/contracts; capability negotiation; harness lifecycle; normalized events/results/errors; compatibility matrix; OpenCode-first implementation; future harnesses without duplicating SI authority.

**Acceptance:** adding a supported harness does not create a second control plane; adapter failures are isolated and observable; portability tests cover contract compatibility.

## Phase 63 — Ecosystem / Marketplace

**Objective:** Establish a governed ecosystem for agents, teams, skills, workflows and extensions.

**Scope:** package metadata; manifests; provenance/signing where appropriate; compatibility/versioning; discovery; install/update/remove; trust levels; security scanning; dependency graph; local/private catalogs; drift detection; deterministic installation ledger.

**Acceptance:** third-party content cannot silently obtain authority; installations are reproducible and auditable; incompatible or unsafe packages are blocked or explicitly quarantined.

## Phase 64 — SDK / Developer Platform

**Objective:** Make SI extensible without weakening core contracts.

**Scope:** typed SDKs; adapter APIs; agent/team/skill/workflow APIs; event APIs; Control API clients; plugin lifecycle; examples; local development tools; contract tests; compatibility/version policy.

**Acceptance:** developers can build extensions against stable contracts; SDK behavior is tested against the same authoritative core; breaking changes are explicit.

## Phase 65 — Workflow + Automation

**Objective:** Deliver a durable visual and programmatic workflow/runbook engine over the real runtime.

**Workflow model:**

```text
Trigger → Condition → Action/Task → Evidence/Gate → Next Task
                                      │
                                      └→ approval / retry / block / continue
```

**Scope:** manual/scheduled/event/queue triggers; DAGs; conditions; branching; loops where bounded; subworkflows; retries; approvals; waits; failure handling; notifications/events; run-once; continue; stop conditions; continuous mode; execution bounds.

**Acceptance:** workflows serialize to typed validated contracts; visual and API-created workflows behave identically; continuous mode is bounded, observable, cancellable and resource-limited.

## Phase 66 — Advanced Web Control Plane

**Objective:** Build the richest SI interface as a polished localhost-first operational product.

**Core areas:** overview; live executions; tasks; agents; teams; workflows; skills; tools/permissions; models; automation; memory/context; governance/approvals; evidence; events; logs; OpenCode; OmniRoute; runtime/workers; system health; settings.

**Advanced UX:** responsive desktop/tablet/mobile layouts; dark/light themes; design system; command palette; global search/navigation; keyboard shortcuts; drag/drop where useful; interactive DAG/workflow canvas; live charts; execution timelines; artifact previews; code/Markdown/JSON viewers; diff viewer; structured log/event viewer; contextual actions; skeleton/loading states; empty/error/recovery states; confirmations; accessibility.

**Live execution:** status, active/queued/completed/failed tasks, agents, model/provider, timing/usage, dependencies, files/artifacts, logs/events, evidence and approvals.

**Controls:** pause, resume, continue, stop, retry where policy permits, approve/deny, inspect/replay evidence/events.

**Acceptance:** Web uses the same Control API and authoritative event/state stream as every other surface; visual workflow editing produces validated contracts; animations communicate state and never become a source of truth; localhost startup/reconnect/error behavior is production-quality.

## Phase 67 — Advanced TUI Control Center

**Objective:** Build a terminal-native live operator cockpit with fast keyboard control.

**Panels:** overview; executions; tasks; agents; teams; workflows; runs; models/providers; automation; memory/context; approvals; events; logs; evidence; system health.

**Capabilities:** live refresh; split panes; trees; fuzzy search; filters; event/log streams; JSON/Markdown/code/diff/artifact inspection; execution timelines; status/progress visualization; pause/resume/continue/stop/retry; approval decisions; reconnect; terminal resize/degradation handling.

**Acceptance:** TUI consumes the same state/event stream and invokes the same Control API as Web; no duplicated business authority exists; long-running work remains readable and operable.

## Phase 68 — Advanced CLI Platform

**Objective:** Build the strongest automation/scripting surface with human, interactive and machine modes.

**Target command families:**

```text
si
si status | doctor | setup | verify | audit | logs | events | config
si agents list | show <agent> | run <agent>
si teams list | show <team> | run <team>
si tasks list | show <task> | pause <task> | resume <task> | stop <task>
si runs list | show <run>
si workflows list | show <workflow> | run <workflow>
si models list | test
si opencode status | setup
si omniroute status | models
```

**Requirements:** consistent terminology/help; `--json`; `--quiet`; `--verbose`; stable exit codes; streaming/log/event modes; safe secret redaction; scripting-friendly selectors; same authority as Web/TUI through Control API; useful interactive behavior for `si` with no arguments.

**Acceptance:** every operational command maps to authoritative SI APIs; machine-readable output is schema-stable and tested; no CLI path bypasses governance.

## Phase 69 — npm Distribution + Setup

**Objective:** Deliver a simple, reliable public installation and onboarding experience.

**Target experience:**

```bash
npm install -g @scinfinite/si
si setup
```

`npx @scinfinite/si` may be supported where technically appropriate.

**Setup responsibilities:** detect OS/runtime/Node/npm; detect or configure SI runtime; detect OpenCode/OmniRoute; validate connectivity; configure safe references; explain missing dependencies; avoid persisting provider secrets unless explicitly required; run health/doctor/verify checks; provide deterministic upgrade/uninstall behavior.

**Acceptance:** clean-machine installation is repeatable; setup is safe and idempotent; failures are actionable; package contents contain no secrets; installation/version state is auditable.

## Phase 70 — End-to-End Production Validation

**Objective:** Prove the complete V4 system as one user-visible product before final hardening.

**Canonical acceptance scenario:**

1. User submits a calculator-building objective through OpenCode.
2. SI recognizes the objective and creates a task graph.
3. SI selects appropriate agents/team members.
4. Independent tasks execute concurrently where permitted.
5. OmniRoute supplies policy-compliant model/provider access.
6. OpenCode remains interactive.
7. Web shows live execution and TUI/CLI show the same authoritative state.
8. User can pause/stop/resume/continue where policy allows.
9. Agents produce evidence and artifacts.
10. Tests/review/verification execute.
11. Final result returns through the OpenCode/SI integration.
12. SI stops when the objective is complete; continuous mode stops on completion, block, approval, resource bound or explicit stop.

**Validation matrix:** runtime; state/events; scheduler; adapters; governance; authorization; evidence; OpenCode; OmniRoute; sessions; memory/context; approvals; waiting/scheduling; security; workspace lifecycle; observability; evaluation; workflow automation; Web; TUI; CLI; npm distribution; recovery; documentation; full CI.

**Acceptance:** clean-machine install plus canonical workload succeeds with captured evidence; failure/recovery, cancellation, restart, approval and budget/security scenarios pass; all required CI gates are green.

## Phase 71 — Final Production Hardening

**Objective:** Close V4 only after the entire platform is hardened, audited and release-ready.

**Scope:** full architecture audit; contract compatibility; security/adversarial testing; performance/load/stress testing; race/concurrency testing; fault injection; restart/recovery; data retention/redaction; dependency audit; packaging audit; docs audit; UX/accessibility audit; cross-surface parity audit; upgrade/rollback testing; clean-machine install; operational runbooks; release checklist; final CI.

**Release gates:**

- No known authority-boundary violation.
- No known secret leakage path.
- No unresolved critical/high runtime or security defect.
- Web/TUI/CLI use the same authoritative state and Control API.
- OpenCode and OmniRoute boundaries remain adapters/downstream services.
- Canonical execution lifecycle and terminality are enforced.
- Evidence supports completion claims.
- Recovery/cancellation/retry behavior is tested.
- Documentation matches the verified implementation.
- Distribution/install/upgrade/uninstall paths are verified.
- Full CI is green on the final release commit.

**Only after these gates pass may V4 be declared complete.**

## 5. Cross-surface capability parity

The three primary interfaces have deliberately different strengths but share one authority:

| Capability | Web | TUI | CLI |
|---|---|---|---|
| Live execution | Rich visual | Fast live cockpit | Stream/JSON |
| Tasks/agents/teams | Full | Full | Full |
| Workflow builder | Visual | Inspect/control | Define/run/automation |
| Approvals | Rich | Fast | Scriptable |
| Logs/events/evidence | Rich viewers | Fast streams | Machine-readable |
| Pause/resume/stop/retry | Full policy-gated | Full policy-gated | Full policy-gated |
| Search/filter | Global/visual | Fuzzy/keyboard | Selectors/flags |
| Automation | Visual | Inspect/control | Strongest scripting |
| Setup/doctor | Guided | Interactive | Primary |

Surface differences are UX choices, not authority differences.

## 6. External reference strategy

SI-Agents continues to study current ECC, Agency Agents, OpenCode, OmniRoute and n8n implementations for useful patterns in agents, skills, hooks, memory, security, sessions, routing, workflows, approvals, observability, packaging and ecosystem design.

Patterns must be generalized and independently implemented. SI-Agents must not become a copy of any reference system, and none of those projects becomes an authority over SI governance or provenance.

## 7. Definition of done for V4

V4 is complete only when Phases 44–71 have individually satisfied their phase gates and the final Phase 71 verification proves the complete product lifecycle:

```text
INSTALL
  → SETUP
  → DISCOVER
  → PLAN
  → AUTHORIZE
  → SCHEDULE
  → EXECUTE IN PARALLEL
  → OBSERVE LIVE
  → CONTROL
  → APPROVE WHEN REQUIRED
  → VERIFY WITH EVIDENCE
  → RETURN RESULT
  → RECOVER/RESUME WHEN NEEDED
  → STOP OR CONTINUE
```

A roadmap item, design document, mock UI, passing unit test or partial integration is not phase completion by itself. Implementation evidence, adversarial/security evidence, documentation and final CI verification are mandatory.
