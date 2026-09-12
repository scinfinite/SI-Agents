# Architecture

SI-Agents V4 uses a single authoritative SI Core. Web, TUI, CLI, OpenCode, runtime adapters, schedulers, agents, teams, workflows, and integrations are clients/adapters of that authority rather than independent state owners.

## V4 target architecture

```text
OpenCode → SI OpenCode Bridge → SI Core / Control API
        → Scheduler / Orchestrator → Tasks / Agents / Teams / Workflows
        → Capability Authorization → OmniRoute → Models / Providers / APIs
        → Results / Artifacts / Evidence → SI Core
        → Observability → Evaluation / Continuous Improvement
        → Release Gates / Canaries / Rollback → OpenCode / Web / TUI / CLI
```

OmniRoute owns model/provider/API routing. SI Core owns execution, orchestration, governance, evidence, lifecycle, persistence, recovery, durable waiting, workspaces, observability, evaluation, and continuous-improvement governance. Evaluation and telemetry remain advisory/governance evidence and never become execution authority.

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
| 61 | Continuous Improvement | **Complete** | PR #75; PR CI #1157 / `34692165853` |

## Phase 61 — continuous improvement

The continuous-improvement authority analyzes evaluation runs into stable failure clusters and regression signals, then creates explainable optimization recommendations for agents, teams, models, routing, and workflows. Recommendations carry expected benefit, confidence, risk, and prerequisites rather than silently mutating runtime state.

Experiments use deterministic subject assignment and bounded variants. Canary promotion is fail-closed on sample size, error rate, cost, latency, and quality. Consequential model/routing/workflow changes require a matching human approval record. Rollback plans retain the previous version and explicit trigger and are only valid for active canary/promoted recommendations.

Improvement history is durable and tamper-evident through a SHA-256 chain. Secret-like data is rejected before persistence. Continuous Improvement is a governance/planning authority only: actual execution continues through the existing SI Core scheduler, capability authorization, deployment/workspace, and runtime authorities.

## Cross-cutting authority contract

Security decisions are fail-closed. Workspace, telemetry, evaluation, and improvement evidence are scoped and bounded. Human decisions and evaluation/improvement outcomes do not become capability grants. Web, TUI, CLI, and OpenCode remain clients of shared SI Core authority. No interface creates competing execution, session, approval, waiting, workspace, observability, evaluation, or improvement state ownership.

## Current position

**V4 Phases 44–61 are closed on `main`; Phase 62 — Cross-Runtime / Cross-Harness is next.**
