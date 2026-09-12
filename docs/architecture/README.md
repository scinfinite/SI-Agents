# Architecture

SI-Agents V4 uses a single authoritative SI Core. Web, TUI, CLI, OpenCode, runtime adapters, schedulers, agents, teams, workflows, and integrations are clients/adapters of that authority rather than independent state owners.

## V4 target architecture

```text
OpenCode → SI OpenCode Bridge → SI Core / Control API
        → Scheduler / Orchestrator → Tasks / Agents / Teams / Workflows
        → Capability Authorization → OmniRoute → Models / Providers / APIs
        → Results / Artifacts / Evidence → SI Core
        → Observability → Evaluation / Release Gates
        → OpenCode / Web / TUI / CLI
```

OmniRoute owns model/provider/API routing. SI Core owns execution, orchestration, governance, evidence, lifecycle, persistence, recovery, durable waiting, workspaces, observability, and evaluation. Evaluation and telemetry remain advisory/governance evidence and never become execution authority.

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
| 52 | Context / Memory Economics | Complete | Final exact-tree CI #1020 / `34673411916` |
| 53 | Persistent Sessions | Complete | Final synchronized-tree mainline CI #1041 / `34675322458` |
| 54 | Human-in-the-Loop | Complete | Final synchronized-tree mainline CI #1051 / `34676632475` |
| 55 | Durable Waiting + Scheduling | Complete | Final synchronized-tree closure CI #1080 / `34678317246` |
| 56 | Intelligent Routing + Economics | Complete | Final synchronized-tree mainline CI #1099 / `34682849381` |
| 57 | Security Platform | Complete | Final synchronized-tree mainline CI #1113 / `34684260315` |
| 58 | Workspace / Worktree Lifecycle | **Advanced hardened** | PR #74; final mainline CI #1144 / `34691176676` |
| 59 | Observability | **Advanced hardened** | PR #74; final mainline CI #1144 / `34691176676` |
| 60 | Evaluation + Benchmarking | **Advanced hardened** | PR #74; final mainline CI #1144 / `34691176676` |

## Phase 58 — workspace / worktree lifecycle

The workspace authority provides tenant/project isolation, optimistic revisions, bounded lease locks, directory and Git-worktree materialization, branch lifecycle, dirty/conflict inspection, deterministic diffs and merge preparation, snapshots and diff artifacts, approved resume, recovery/cleanup, path and symlink defenses, tamper-evident lifecycle evidence, and bounded garbage-collection discovery. Advanced hardening adds adversarial event-chain tamper detection and authorization-callback verification. Workspace state does not grant credentials, capabilities, provider access, or execution identity.

## Phase 59 — observability

The observability authority provides bounded structured logs/events/metrics/spans, shared security-scanner secret detection plus redaction, integrity evidence across the full bounded integrity scan, correlation/causation, trace timelines, live-feed retention, percentile metrics, operator health, JSONL export, and tenant/project filtering. Telemetry is evidence only; it cannot grant authorization or execution authority.

## Phase 60 — evaluation + benchmarking

The evaluation authority provides deterministic golden cases, exact/normalized/containment/JSON/tolerance/rubric scoring, weighted multi-metric dimensions, reliability/security/latency/cost measurements, explicit failure taxonomy, fail-closed scoring, bounded evidence, benchmark history, regression detection, human review, deterministic weighted experiments, cryptographic report digests, and configurable release gates. Advanced hardening makes documented cost/latency budgets enforceable, rejects secret-bearing evaluator outputs/metadata/review rationale, verifies persisted evidence integrity, tightens experiment inputs, and fails closed on empty reports. Evaluation remains advisory and cannot grant execution, credentials, provider access, or approvals.

## Cross-cutting authority contract

Security decisions are fail-closed. Workspace, telemetry, and evaluation evidence are scoped and bounded. Human decisions and evaluation outcomes do not become capability grants. Web, TUI, CLI, and OpenCode remain clients of shared SI Core authority. No interface creates competing execution, session, approval, waiting, workspace, observability, or evaluation state ownership.

## Current position

**V4 Phases 44–60 are complete at the required advanced-hardening level on `main`. Phase 61 — Continuous Improvement is next.**

The advanced-hardening implementation was merged through PR #74. Its PR CI #1143 (`34691131729`) passed, and the synchronized-tree mainline CI #1144 (`34691176676`) passed repository audit, distribution/wheel verification, integration verification, Ruff, and the full test suite.
