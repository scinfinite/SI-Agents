# Architecture

SI-Agents V4 uses a single authoritative SI Core. Web, TUI, CLI, OpenCode, runtime adapters, schedulers, agents, teams, workflows, and integrations are clients/adapters of that authority rather than independent state owners.

## V4 target architecture

```text
OpenCode → SI OpenCode Bridge → SI Core / Control API
        → Scheduler / Orchestrator → Tasks / Agents / Teams / Workflows
        → Authorization → OmniRoute → Models / Providers / APIs
        → Results / Artifacts / Evidence → SI Core
        → OpenCode / Web / TUI / CLI
```

OmniRoute owns model/provider/API routing. SI Core owns execution, orchestration, governance, evidence, lifecycle, persistence, and recovery.

## Verified V4 phases

| Phase | Capability | Status | Evidence |
|---:|---|---|---|
| 44 | Execution Runtime Foundation | Complete | CI #919 / `34610448789` |
| 45 | Event Bus + State Architecture | Complete | CI #935 / `34612616978` |
| 46 | Parallel Scheduler + Executor | **Advanced hardened** | Hardening CI #984 / `34671292491` |
| 47 | OpenCode Bridge | **Advanced hardened** | Hardening CI #984 / `34671292491` |
| 48 | OmniRoute Integration | Complete | CI #949 / `34623762921` |
| 49 | Agent + Team Builder | **Advanced hardened** | Hardening CI #984 / `34671292491` |
| 50 | Capability Authorization | **Advanced hardened** | Hardening CI #984 / `34671292491` |
| 51 | Checkpoints + Resume | Complete | CI #977 / `34627956634` |

## Advanced hardening status

- **Phase 46:** explicit execution identity conflict safety, scheduler/runtime idempotency, DAG cycle defense, bounded parallelism, durable recovery, cancellation finalization, dependency propagation, and authority boundaries.
- **Phase 47:** request timeout propagation, bounded 1 MiB SSE frames, strict terminal streaming semantics, cancellation, session filtering, error normalization, loopback-default security, and authority boundaries.
- **Phase 49:** schema-versioned deterministic catalogs/manifests, stronger definition/metadata validation, acyclic handoffs, deterministic topological execution layers, bounded team composition, and declaration/runtime authority separation.
- **Phase 50:** request-fingerprint-bound approvals, replay prevention, secret-like metadata rejection, bounded governance inputs, explicit/fail-closed egress, declared-capability enforcement, scope checks, and cost/risk controls.

Combined hardening CI **#984 (`34671292491`)** passed distribution, wheel verification, repository audit, integration verification, Ruff, and full pytest. The post-merge mainline CI remains the authoritative exact-tree closure gate.

## Phase 51 authority rules

Checkpoints are progress evidence, not authority. Their snapshots cannot restore credentials, capabilities, grants, provider authorization, or identity. Resume is performed through `ExecutionStore.new_attempt()` after checkpoint integrity, lineage, execution identity, and terminal-state checks.

## Planned V4 architecture layers — Phases 52–71

| Phase | Architectural layer | Key outcome |
|---:|---|---|
| 52 | Context / Memory Economics | Efficient, permission-aware context and memory with token/cost controls |
| 53 | Persistent Sessions | Durable sessions spanning tasks, agents, workflows, models and interfaces |
| 54 | Human-in-the-Loop | First-class approvals, human input, review and escalation |
| 55 | Durable Waiting + Scheduling | Durable waits, timers, triggers and long-running scheduling |
| 56 | Intelligent Routing + Economics | Quality/cost/latency/reliability-aware orchestration around OmniRoute |
| 57 | Security Platform | Unified identity, capability, secret, tool, egress and injection controls |
| 58 | Workspace / Worktree Lifecycle | Isolated and recoverable development workspaces/Git worktrees |
| 59 | Observability | Live state, logs, metrics, traces, timelines and evidence |
| 60 | Evaluation + Benchmarking | Measurable quality, reliability, security, cost and regression evaluation |
| 61 | Continuous Improvement | Controlled evaluation-to-improvement loop with rollback/evidence |
| 62 | Cross-Runtime / Cross-Harness | Harness-neutral contracts and adapters |
| 63 | Ecosystem / Marketplace | Governed extension/package ecosystem |
| 64 | SDK / Developer Platform | Stable APIs and Python/TypeScript developer access |
| 65 | Workflow + Automation | Durable visualizable automation, triggers and integrations |
| 66 | Advanced Web Control Plane | Rich localhost operational control and live visualization |
| 67 | Advanced TUI Control Center | Terminal-native live operator cockpit |
| 68 | Advanced CLI Platform | Stable human/machine CLI and automation interface |
| 69 | npm Distribution + Setup | One-command installation and OpenCode/OmniRoute setup |
| 70 | End-to-End Production Validation | Full real-user, failure, security, recovery, UI and install validation |
| 71 | Final Production Hardening | Final release/security/reliability/UX/package gate |

## V4 surface contract

### Web

Localhost-first and richest interface. Planned capabilities include live execution/agent/task/team status, interactive DAG/workflow canvas, timelines, events, logs, evidence, artifacts, code/Markdown/JSON/diff viewers, routing/cost/health, approvals, search, global navigation, command palette, keyboard shortcuts, responsive desktop/tablet/mobile layouts, accessibility, and state-oriented animation.

### TUI

Terminal-native operator cockpit with live refresh/streams, split panes, trees, DAG/progress views, fuzzy search/filtering, inspection, approvals, pause/resume/stop/retry/cancel/reconnect, and degraded-mode operation.

### CLI

Stable human and machine interface with normal commands, JSON schemas, exit codes, streaming, CI/non-interactive mode, profiles, authentication, local/remote control, session/execution attachment, and scripting.

All surfaces operate on the same SI Core authority.

## Next

**Phase 52 — Context / Memory Economics.**

See `SI_AGENTS_V4_PLAN.md` for the complete detailed feature specification and `PHASES.md` for status/evidence and closure rules.
