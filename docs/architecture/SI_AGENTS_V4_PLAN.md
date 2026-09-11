# SI-Agents v4 — Agent Operating System Plan

**Status:** Planning / architecture baseline
**Baseline:** SI-Agents v3, Phases 1–43 complete and CI-verified
**Planned sequence:** Phases 44–55
**Primary product goal:** Turn SI-Agents from a strong governance/control surface into a real agent operating system with persistent execution, parallel orchestration, live control, first-class OpenCode + OmniRoute integration, and a simple npm-based installation experience.

> **Planning rule:** This document defines the intended v4 direction. It does not claim an implementation is complete. A phase is complete only after implementation, tests, security/adversarial checks, documentation, packaging where relevant, and final CI verification provide evidence.

---

## 1. Executive vision

SI-Agents v4 should make multi-agent development feel like one coherent system rather than a collection of independent tools.

The intended user experience is:

```text
                    ┌─────────────────────────┐
                    │        SI Web            │
                    │ Primary control plane    │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   SI Control API        │
                    │ Single source of truth  │
                    └────────────┬────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
        ┌─────▼─────┐      ┌─────▼─────┐      ┌────▼─────┐
        │ SI Core   │      │ Scheduler │      │ Event Bus│
        │ Registry  │      │ Executor  │      │  State   │
        └─────┬─────┘      └─────┬─────┘      └────┬─────┘
              │                  │                  │
              └──────────────────┼──────────────────┘
                                 │
                       ┌─────────▼─────────┐
                       │ OpenCode Bridge   │
                       └─────────┬─────────┘
                                 │
                              OpenCode
                                 │
                             OmniRoute
                                 │
                         Models / Providers

       TUI = live operator control surface
       CLI = automation / scripting control surface
```

### Product principles

1. **One Core, one authority.** Web, TUI, CLI, and integrations operate through the same SI Core/Control API and never create competing execution state.
2. **Web-first control.** The Web application is the primary configuration and operational control plane.
3. **OpenCode remains the interactive coding harness.** SI orchestrates work around it rather than replacing it.
4. **OmniRoute remains model/provider routing infrastructure.** SI consumes that capability rather than becoming another provider router.
5. **Parallelism is real.** Independent tasks must be able to execute concurrently with explicit limits and dependency handling.
6. **State is persistent and observable.** Users must be able to understand what is running, why, by whom, using which model, and what evidence was produced.
7. **Control is reversible where possible.** Pause, resume, continue, stop, cancellation, retry, and approval gates are explicit state transitions.
8. **Evidence before completion.** An agent saying it finished is not sufficient; tests, artifacts, logs, and verification gates must establish completion.
9. **Secure by default.** Credentials remain outside SI state where possible; permissions and authority boundaries fail closed.
10. **Simple installation.** The target public installation experience is `npm install -g @scinfinite/si`, followed by a guided setup flow.
11. **Preserve v3 contracts.** Existing personas, skills, governance, memory, organization, and control-plane capabilities evolve without silently reopening the completed v3 sequence.
12. **No blind copying.** External projects such as ECC and Agency Agents may provide engineering patterns and research input, but SI implementations remain independently designed and governed.

---

## 2. Current baseline and transition

SI-Agents v3 is closed. Its architecture already establishes one SI Core, one Control API, and multiple operator/harness surfaces. The v4 effort should therefore extend the existing system rather than replace it wholesale.

The key transition is:

```text
v3:
Governance + catalogs + configuration + control surfaces

                ↓

v4:
Persistent runtime + event/state model + scheduler + live orchestration
                +
OpenCode/OmniRoute integration + polished Web/TUI/CLI + npm distribution
```

The most important architectural decision is to build the execution/runtime foundation before investing heavily in presentation surfaces. Otherwise Web/TUI/CLI risk becoming increasingly sophisticated dashboards over incomplete execution semantics.

---

## 3. Target system model

### 3.1 Core domains

The v4 core should establish explicit domains/contracts for:

- **Agent Registry** — agents/personas, capabilities, constraints, models, tools, permissions.
- **Team Registry** — reusable teams, composition, roles, concurrency and evidence policy.
- **Skill Registry** — portable capabilities and their machine-readable contracts.
- **Workflow Registry** — DAGs/runbooks, triggers, conditions, actions, gates, continuation policy.
- **Task Manager** — task identity, lifecycle, dependencies, ownership, attempts, results.
- **Execution Manager** — runs, workers, cancellation, pause/resume, retries, resource controls.
- **Scheduler** — dependency resolution, ready queue, concurrency, fairness and prioritization.
- **Event Bus** — durable/ordered operational events and subscriptions.
- **State Store** — authoritative execution state and projections.
- **Evidence Store** — test results, artifacts, logs, verification records and completion evidence.
- **Governance Engine** — permissions, approval gates, policy evaluation, fail-closed decisions.
- **OpenCode Bridge** — session/task/status/result integration boundary.
- **OmniRoute Adapter** — model/provider discovery and request integration boundary.
- **Automation Engine** — schedules, event triggers, continuous mode and chained workflows.

### 3.2 Canonical identifiers

Every runtime object should use stable identifiers and explicit relationships:

- `execution_id`
- `workflow_id`
- `task_id`
- `agent_id`
- `team_id`
- `session_id`
- `attempt_id`
- `event_id`
- `evidence_id`
- `artifact_id`

Parent/child relationships must be explicit so a user can navigate from a run to its workflow, tasks, agents, attempts, events and evidence.

### 3.3 Lifecycle state machine

The runtime should use explicit, validated transitions rather than ad-hoc booleans.

```text
QUEUED → PLANNING → READY → RUNNING
                         │       │
                         │       ├──→ PAUSED ──→ RUNNING
                         │       │
                         │       ├──→ FAILED ──→ RETRY → READY
                         │       │
                         │       ├──→ CANCELLED
                         │       │
                         │       └──→ COMPLETED → NEXT TASK
                         │
                         └──→ BLOCKED → READY
```

The exact transition matrix must be defined and tested in Phase 44/45. Invalid transitions must fail closed.

---

# 4. Phase roadmap

## Phase 44 — Execution Runtime Foundation

### Objective
Create the persistent runtime primitives required for real agent execution.

### Scope

- Execution/run model.
- Task model and lifecycle state machine.
- Agent/team/workflow references.
- Persistent execution state.
- Attempt tracking.
- Cancellation primitives.
- Pause/resume primitives.
- Timeout abstraction.
- Resource ownership and cleanup.
- Runtime API contracts.
- Deterministic state transitions.
- Runtime unit/integration tests.

### Acceptance criteria

- A workflow can create an execution and tasks with stable IDs.
- State survives process restart.
- Invalid transitions are rejected.
- Pause/stop/resume semantics are deterministic.
- Cancellation cleans up owned resources.
- Runtime state is exposed through the existing Control API without duplicating authority.

---

## Phase 45 — Event Bus + State Architecture

### Objective
Make execution observable and synchronize every control surface through authoritative events/state.

### Scope

- Typed event envelope.
- Event IDs and timestamps.
- Correlation/causation IDs.
- Event persistence/retention policy.
- State projections/read models.
- Subscriptions/streaming.
- Agent/task/run status events.
- Evidence events.
- Governance/approval events.
- Error and retry events.
- Reconnection and replay semantics.

### Required event examples

```text
execution.created
execution.started
execution.paused
execution.resumed
execution.stopped
execution.completed
execution.failed

task.queued
task.ready
task.started
task.paused
task.retrying
task.completed
task.failed

agent.started
agent.progress
agent.completed
agent.failed

evidence.created
approval.required
approval.granted
approval.denied
```

### Acceptance criteria

Web, TUI, CLI and OpenCode integration can observe the same execution state without maintaining separate truth.

---

## Phase 46 — Parallel Scheduler + Executor

### Objective
Turn the runtime into a real multi-task execution engine.

### Scope

- DAG/task graph representation.
- Dependency resolution.
- Ready queue.
- Worker pools.
- Configurable maximum concurrency.
- Parallel fan-out.
- Fan-in/join semantics.
- Retries with bounded policy.
- Timeouts.
- Cancellation propagation.
- Failure recovery.
- Resource limits.
- Priority/fairness policy.
- Approval gates.
- Idempotency protection.

### Target behavior

```text
                    Workflow
                       │
              ┌────────┼────────┐
              ▼        ▼        ▼
           Task A    Task B    Task C
              │        │        │
              └────────┼────────┘
                       ▼
                   Review D
                       │
                    Verify E
```

A, B and C must execute concurrently when dependencies and concurrency limits permit. D must not start until its prerequisites satisfy their completion policy.

### Acceptance criteria

- Independent tasks demonstrably run in parallel.
- Dependent tasks wait correctly.
- A failed task follows its configured retry/recovery policy.
- Stop/cancel propagates safely.
- Concurrency never exceeds configured limits.
- Scheduler behavior is deterministic under test.

---

## Phase 47 — OpenCode Bridge

### Objective
Make OpenCode a first-class interactive harness connected to SI runtime state.

### Scope

- Inspect current OpenCode protocol/session/ACP capabilities before implementation.
- Define a versioned SI ↔ OpenCode integration contract.
- Session association.
- Task submission.
- Execution status.
- Live events/progress.
- Pause/resume/stop/continue controls where supported.
- Result delivery.
- Error propagation.
- Reconnect/recovery behavior.
- Capability negotiation.
- Secure local integration.

### Canonical relationship

```text
OpenCode
   │ user prompt
   ▼
SI Bridge
   │
SI Runtime / Scheduler
   │
Agents / Tasks
   │
result + evidence
   ▼
OpenCode
```

The bridge must use the current supported OpenCode integration mechanisms discovered during implementation. It must not invent undocumented coupling.

### Acceptance criteria

A user can initiate an SI-managed objective from OpenCode and receive live status plus the final result without manually copying execution state between systems.

---

## Phase 48 — OmniRoute Integration

### Objective
Make OmniRoute the model/provider access layer used by SI-managed execution without turning SI into a competing router.

### Scope

- OmniRoute health/status integration.
- Model catalog discovery.
- Model policy abstraction.
- Preferred/fallback model selection.
- Capability-aware model selection.
- Request routing adapter.
- Error/rate-limit handling.
- Usage metadata where available.
- Credential references without storing secrets.
- OpenCode + OmniRoute + SI interoperability tests.

### Acceptance criteria

SI can identify usable models through the configured OmniRoute boundary and execute the canonical workload through the OpenCode → SI → OmniRoute path.

---

## Phase 49 — Web 2.0: Primary Control Plane

### Objective
Replace the current limited Web experience with a polished, live, production-quality control center backed by the real runtime.

### Core areas

- Overview dashboard.
- Live executions.
- Tasks.
- Agents/personas.
- Teams.
- Workflows/runbooks.
- Skills.
- Tools and permissions.
- Models/model policies.
- Automation.
- Memory/knowledge controls.
- Governance/approvals.
- Evidence.
- Events.
- Logs.
- OpenCode integration.
- OmniRoute integration.
- Runtime/worker settings.
- System health.

### Live execution view

Each run should expose:

- Current phase/status.
- Active agents.
- Queued tasks.
- Completed tasks.
- Failed/blocked tasks.
- Current task per agent.
- Model/provider.
- Time and usage metrics when available.
- Files/artifacts touched.
- Logs/events.
- Evidence.
- Dependencies.
- Parent/child tasks.
- Approval requirements.

### Operator controls

- Pause.
- Resume.
- Continue.
- Stop.
- Retry where policy permits.
- Approve/deny gated actions.
- Inspect logs/events/evidence.

### UX principle

The Web UI should feel like a coherent product, not a collection of API forms. Visual quality, information hierarchy, responsiveness, accessibility, error states and loading states are part of the acceptance criteria.

---

## Phase 50 — TUI 2.0: Terminal Control Center

### Objective
Turn the TUI into a serious live operator console sharing exactly the same SI state and controls as Web.

### Primary panels

- Overview.
- Tasks.
- Agents.
- Teams.
- Workflows.
- Runs.
- Models.
- Automation.
- Memory.
- Events.
- Logs.

### Interaction model

```text
↑ / ↓       Navigate
Enter       Details
Tab         Panels
P           Pause
R           Resume
S           Stop
C           Continue
L           Logs
E           Events
A           Agents
T           Tasks
W           Workflows
M           Models
Q           Quit
```

The exact bindings may evolve during implementation, but the TUI must support fast keyboard-first operation and clear live updates.

### Acceptance criteria

- TUI updates from the same event/state stream as Web.
- Operator controls invoke the same Control API.
- No duplicated business logic exists in the TUI.
- Long-running executions remain readable and navigable.
- Terminal degradation/resize/reconnect is handled gracefully.

---

## Phase 51 — CLI 2.0

### Objective
Create a coherent command-line product for operators, automation and scripts.

### Target command tree

```text
si
si status
si doctor
si setup
si verify
si audit
si logs
si events
si config

si agents list
si agents show <agent>
si agents run <agent>

si teams list
si teams show <team>
si teams run <team>

si tasks list
si tasks show <task>
si tasks pause <task>
si tasks resume <task>
si tasks stop <task>

si runs list
si runs show <run>

si workflows list
si workflows show <workflow>
si workflows run <workflow>

si models list
si models test

si opencode status
si opencode setup

si omniroute status
si omniroute models
```

### CLI requirements

- Consistent help and terminology.
- Machine-readable `--json` output for operational commands.
- `--quiet` and `--verbose` where appropriate.
- Stable exit codes.
- No secrets printed.
- Same authority as Web/TUI through Control API/core.
- Useful interactive behavior for `si` with no arguments where appropriate.

---

## Phase 52 — Agent + Team Builder

### Objective
Make agent and team configuration genuinely manageable from the Web control plane while preserving SI-native governance and typed contracts.

### Agent configuration

- Identity/persona.
- Capabilities.
- Skills.
- Tool permissions.
- Model policy.
- Resource limits.
- Governance requirements.
- Evidence policy.
- Runtime constraints.

### Team configuration

- Member agents.
- Roles.
- Task routing.
- Parallelism.
- Dependencies.
- Evidence requirements.
- Approval gates.
- Failure/retry policy.

### Safety

Web-created configurations must produce validated machine contracts. Imported text must never silently grant permissions or execution authority.

---

## Phase 53 — Workflow + Automation

### Objective
Provide reusable runbooks and continuous automation over the real runtime.

### Workflow model

```text
Trigger
  ↓
Condition
  ↓
Action / Task
  ↓
Evidence / Gate
  ↓
Next Task
  ↓
Condition
  ↓
Continue / Complete / Block
```

### Automation capabilities

- Manual trigger.
- Scheduled trigger.
- Event trigger.
- Queue-based trigger.
- Conditional branching.
- Retry policy.
- Approval gates.
- Failure handling.
- Notifications/events.
- Continuous mode.
- Run-once mode.
- Continue mode.
- Stop conditions.
- Maximum execution bounds.

### Continuous mode

Continuous mode must not mean uncontrolled infinite execution. It requires explicit boundaries, observable progress, cancellation, resource limits and a clear completion/blocked/approval-required state.

---

## Phase 54 — npm Distribution + Setup Wizard

### Objective
Make SI-Agents simple to install and start, especially for users who should not need to understand Python environments.

### Target installation

```bash
npm install -g @scinfinite/si
```

A zero-install alternative may be supported where useful:

```bash
npx @scinfinite/si
```

### Guided setup

```bash
si setup
```

The setup flow should:

1. Detect the operating environment.
2. Detect Node/npm prerequisites.
3. Detect SI runtime requirements.
4. Detect OpenCode.
5. Detect OmniRoute.
6. Validate connectivity where possible.
7. Configure integration references safely.
8. Create only required local state.
9. Avoid storing provider credentials in SI unless explicitly required by a future contract.
10. Explain any missing optional dependency clearly.
11. Run a final health/verification check.

### Distribution architecture

The public package may use Node as the installation/bootstrap layer while keeping internal runtime components in Python or another implementation language where that remains technically appropriate. The user-facing installation experience should hide unnecessary environment complexity.

### Acceptance criteria

A supported clean environment can install SI using the npm package, run `si doctor`, complete guided setup, and reach a verified ready state without manual virtual-environment creation or hand-editing JSON.

---

## Phase 55 — End-to-End Production Validation

### Objective
Prove that v4 works as one system rather than as individually passing components.

### Canonical calculator scenario

This is the primary acceptance benchmark:

```text
1. User enters a calculator-building request in OpenCode.
2. SI recognizes the objective.
3. SI creates a task graph.
4. SI selects appropriate agents/team members.
5. Independent tasks execute concurrently where possible.
6. OmniRoute provides model/provider access.
7. OpenCode remains interactive.
8. Web shows live execution state.
9. User can pause/stop/resume/continue.
10. Agents produce evidence.
11. Tests and review tasks execute.
12. Final result returns to OpenCode.
13. SI stops automatically when the objective is complete.
14. In continuous mode, SI proceeds to the next eligible task until completion, blocking, approval, or explicit stop.
```

### Validation matrix

| Area | Required proof |
|---|---|
| Runtime | Persistent state and valid lifecycle transitions |
| Events | Live, correlated execution events |
| Scheduler | Real bounded parallel execution |
| Governance | Permission/approval gates fail closed |
| Evidence | Completion is backed by artifacts/tests/evidence |
| OpenCode | Initiation, status and result integration |
| OmniRoute | Model discovery/request path works |
| Web | Live dashboard and operational controls |
| TUI | Live terminal control and monitoring |
| CLI | Stable commands, JSON output and exit codes |
| Automation | Run once, continue and continuous modes |
| Distribution | npm install + guided setup |
| Recovery | Retry, timeout, cancellation and restart behavior |
| Security | No secret leakage; authority boundaries enforced |
| Documentation | Current behavior accurately documented |
| CI | Full repository verification green |

---

# 5. Cross-phase engineering requirements

## Testing

Every phase must add tests for its new contracts and preserve existing tests. Runtime and scheduler work should include deterministic unit tests plus integration tests for lifecycle, concurrency, restart, cancellation and failure paths.

## Security

- Never print or commit credentials.
- Do not persist provider secrets unnecessarily.
- Validate imported configurations.
- Fail closed on unknown authorities/targets.
- Enforce tool/resource permissions at the runtime boundary.
- Treat Web/TUI/CLI as clients, not trusted execution authorities.
- Audit dangerous transitions and approval decisions.

## Observability

Every meaningful state transition should be attributable to an execution, task, agent and/or workflow where applicable. Events should provide enough correlation information to reconstruct what happened.

## Compatibility

Existing v3 contracts should remain stable unless a v4 change is explicitly versioned and migrated. Backward compatibility should be preferred for configuration and read APIs when it does not compromise correctness or security.

## Performance

Concurrency must be bounded and measurable. Avoid designs that require an unbounded number of processes, threads, events or retained logs. The system should degrade predictably under load.

## Failure handling

Failures must be explicit states, not silent disappearance. Retry behavior must be bounded and policy-driven. Cancellation must be distinguishable from failure. A restart must not corrupt authoritative state.

## Documentation

Documentation must follow implementation and CI evidence. Phase documents should record exact acceptance criteria, tests, verification results, migrations and known limitations.

---

# 6. External engineering references

SI-Agents should continue to study current ECC and Agency Agents material as external engineering references. Useful patterns may include:

- harness-neutral session/state adapters;
- specialized agent delegation;
- orchestrator/runbook patterns;
- continuous-agent-loop concepts;
- hook and supply-chain hardening;
- agent manifests and governance contracts;
- division/team consistency workflows;
- installer/control surfaces;
- one-click runbooks and reusable agent teams.

These references are inputs to design review, not dependencies or sources of copied implementation. Each adopted idea must be independently specified, tested and checked against SI's authority, provenance and governance model.

---

# 7. Dependency and implementation order

The intended dependency chain is:

```text
44 Runtime
   ↓
45 Event + State
   ↓
46 Scheduler / Executor
   ↓
47 OpenCode Bridge ───┐
   ↓                  │
48 OmniRoute ─────────┘
   ↓
49 Web 2.0
   ↓
50 TUI 2.0
   ↓
51 CLI 2.0
   ↓
52 Agent / Team Builder
   ↓
53 Workflow / Automation
   ↓
54 npm Distribution / Setup
   ↓
55 End-to-End Production Validation
```

Some implementation work may proceed in parallel after contracts are stable, but presentation-layer work must not become a substitute for the runtime foundation.

---

# 8. Definition of v4 complete

SI-Agents v4 should not be declared complete because the Web looks polished or because individual tests pass. Completion requires the whole operating model to work together.

The release gate is:

```text
INSTALL
  ↓
SETUP
  ↓
DISCOVER
  ↓
PLAN
  ↓
SCHEDULE
  ↓
EXECUTE IN PARALLEL
  ↓
OBSERVE LIVE
  ↓
CONTROL
  ↓
VERIFY WITH EVIDENCE
  ↓
RETURN RESULT
  ↓
STOP OR CONTINUE
```

The canonical calculator scenario must demonstrate this path across OpenCode, SI Core, Scheduler, agents, OmniRoute, Web, TUI and CLI with persistent state, live events, governance, evidence and recovery behavior.

Only after final CI verification is green, documentation is synchronized with implementation, and the end-to-end acceptance matrix is satisfied should the v4 sequence be declared complete.

---

# 9. Immediate next step

Before Phase 44 implementation begins:

1. Re-verify that Phase 43 is closed on `main` and that current CI remains green.
2. Inspect the current SI runtime/control API implementation to identify reusable v3 contracts.
3. Inspect current OpenCode integration/protocol capabilities and current OmniRoute interfaces rather than assuming APIs.
4. Freeze the v4 runtime/event/state contracts.
5. Implement Phase 44 with tests before building higher-level surfaces.

**Planning status:** ready for Phase 44 architecture review and implementation.