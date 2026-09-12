# Documentation

## Current V4 baseline

SI-Agents V4 has completed Phases **44–51**. Phases **46, 47, 49, and 50** have additionally passed an advanced-level hardening audit. **Phase 52 — Context / Memory Economics** is under implementation and is the active phase.

## V4 architecture and roadmap

- `architecture/SI_AGENTS_V4_PLAN.md` — authoritative V4 product vision, detailed Phases 52–71 scope, interface contract, authority model, and closure gates.
- `architecture/PHASES.md` — phase sequence, current status, evidence, advanced-hardening markers, and documentation closure rules.
- `architecture/README.md` — architecture status and current verified capabilities.
- `architecture/CONTEXT_MEMORY.md` — context/memory authority boundaries, budget hierarchy, selection invariants, and auditability.

The V4 target is one authoritative SI Core shared by Web, TUI, CLI, OpenCode, runtime adapters, schedulers, agents, teams, workflows, and integrations.

## Current implementation evidence

| Phase | Current status | Evidence |
|---:|---|---|
| 44 | Complete | CI #919 / `34610448789` |
| 45 | Complete | CI #935 / `34612616978` |
| 46 | **Advanced hardened** | Hardening CI #984 / `34671292491` |
| 47 | **Advanced hardened** | Hardening CI #984 / `34671292491` |
| 48 | Complete | CI #949 / `34623762921` |
| 49 | **Advanced hardened** | Hardening CI #984 / `34671292491` |
| 50 | **Advanced hardened** | Hardening CI #984 / `34671292491` |
| 51 | Complete | CI #977 / `34627956634` |
| 52 | **In implementation** | Context economics contracts, implementation, adversarial tests and architecture docs are on the active Phase 52 branch; final mainline CI remains the closure gate. |

## Advanced hardening

Combined advanced CI **#984 (`34671292491`)** passed distribution, wheel verification, repository audit, integration verification, Ruff, and the complete pytest suite.

- Phase 46: scheduler identity/idempotency, DAG cycle safety, bounded concurrency, recovery and cancellation.
- Phase 47: request timeout propagation, 1 MiB SSE frame bound, strict terminal streaming, cancellation, session filtering and transport/error safety.
- Phase 49: schema-versioned deterministic catalogs/manifests, validation, acyclic handoffs and deterministic execution layers.
- Phase 50: request-fingerprint-bound approvals, replay prevention, secret-like metadata rejection, bounded inputs and fail-closed egress.

## V4 product surfaces

### Web

Localhost-first and richest control plane. Planned V4 scope includes live execution/agent/task/team status, interactive DAG/workflow canvas, timelines, logs, events, artifacts, code/Markdown/JSON/diff viewers, approvals, routing/cost/health views, search, command palette, keyboard shortcuts, responsive layouts, accessibility, and meaningful state animations.

### TUI

Terminal-native operator cockpit with live streams, split panes, trees, DAG/progress views, fuzzy search/filtering, JSON/diff/artifact/log/event inspection, approvals, pause/resume/stop/retry/cancel/reconnect, and degraded-mode handling.

### CLI

Stable human and machine interface with interactive commands, JSON schemas, exit codes, streaming, CI/non-interactive mode, profiles, authentication, local/remote control, and scripting support.

All three surfaces operate on the same authoritative SI Core state.

## Active and planned Phases 52–71

- **52 — Context / Memory Economics:** context budgets, memory layers, retrieval, relevance, compaction, deduplication, privacy, token/cost economics. **Active implementation:** deterministic selection contracts, model input capacity, sensitivity/secret controls, cost accounting, compaction, provenance/evidence, and atomic snapshots.
- **53 — Persistent Sessions:** durable sessions, history, context/memory, recovery, replay, export/import, branching, cross-interface continuity.
- **54 — Human-in-the-Loop:** approvals, human input, review gates, escalation, controlled resume, audit/evidence, Web/TUI/CLI controls.
- **55 — Durable Waiting + Scheduling:** durable waits, timers, schedules, triggers, retry/backoff, restart-safe waiting, fairness and long-running workflows.
- **56 — Intelligent Routing + Economics:** task/model matching, quality/latency/reliability/cost routing, fallbacks, budgets, forecasting and route evidence.
- **57 — Security Platform:** least privilege, identity, secrets, tool/MCP/provider/filesystem/network controls, injection defenses, scanning and audit.
- **58 — Workspace / Worktree Lifecycle:** workspace/worktree/branch isolation, locking, diffs, merge preparation, artifacts, cleanup, recovery and audit.
- **59 — Observability:** live status, metrics, traces, structured logs, timelines, tool/model calls, cost/resource views, evidence and operator health.
- **60 — Evaluation + Benchmarking:** golden tasks, scenarios, quality/reliability/security/cost benchmarks, scoring, regression gates and A/B evaluation.
- **61 — Continuous Improvement:** failure analysis, optimization proposals, experiments, versioning, canaries, rollback and evidence-backed improvement loop.
- **62 — Cross-Runtime / Cross-Harness:** common contracts and adapters for runtimes, sessions, tools, models, events, capabilities, context, checkpoints and artifacts.
- **63 — Ecosystem / Marketplace:** governed agents, skills, tools, teams, workflows, integrations, manifests, dependencies, provenance, security and drift control.
- **64 — SDK / Developer Platform:** Python and TypeScript/JavaScript SDKs, REST, WebSocket/SSE, stable schemas, auth, idempotency, webhooks and developer tooling.
- **65 — Workflow + Automation:** durable DAGs, conditions, loops, delegation, human gates, waits, timers, triggers, retries, compensation, rollback, templates and integrations.
- **66 — Advanced Web Control Plane:** complete localhost operational control, live status, DAGs, timelines, artifacts, diffs, logs, approvals, search, command palette and responsive/accessibility UX.
- **67 — Advanced TUI Control Center:** full terminal operator cockpit with live state, inspection, control, approvals, streams, recovery and debugging.
- **68 — Advanced CLI Platform:** stable human/machine CLI, JSON, exit codes, streaming, CI automation, profiles, session attachment and remote/local control.
- **69 — npm Distribution + Setup:** one-command installation, bootstrap, platform detection, setup wizard, OpenCode/OmniRoute integration, health checks, upgrade/uninstall and clean-machine validation.
- **70 — End-to-End Production Validation:** real OpenCode→SI→OmniRoute→model/provider→SI flow plus multi-agent, recovery, security, UI, workflow and installation scenarios.
- **71 — Final Production Hardening:** final architecture/security/reliability/concurrency/persistence/UX/API/package audit and release evidence.

## Phase 51 authority rules

Checkpoints are progress evidence, not authority. Snapshots cannot restore credentials, capabilities, grants, provider authorization, or identity. Resume is performed through `ExecutionStore.new_attempt()` after checkpoint integrity, lineage, execution identity, and terminal-state checks.

## Phase closure rule

After every phase and every cross-phase hardening audit, implementation evidence, security/adversarial coverage, documentation, current/index documents, and CI verification are synchronized. The final exact-tree mainline CI gate is required before a change is considered permanently closed on `main`.
