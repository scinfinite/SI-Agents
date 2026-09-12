# Architecture

SI-Agents V4 uses a single authoritative SI Core. Web, TUI, CLI, OpenCode, runtime adapters, schedulers, agents, teams, workflows, and integrations are clients/adapters of that authority rather than independent state owners.

## V4 target architecture

```text
OpenCode / Web / TUI / CLI → SI Core / Control API
                          → Scheduler / Orchestrator
                          → Tasks / Agents / Teams / Workflows
                          → Capability Authorization → OmniRoute
                          → Models / Providers / APIs
                          → Results / Artifacts / Evidence
                          → Observability → Evaluation → Continuous Improvement
                          → Release Gates / Canaries / Rollback → Clients
```

OmniRoute owns model/provider/API routing. SI Core owns execution, orchestration, governance, evidence, lifecycle, persistence, recovery, waiting, workspaces, observability, evaluation, and continuous-improvement governance.

## Verified V4 phases

| Phase | Capability | Status |
|---:|---|---|
| 44 | Execution Runtime Foundation | Complete |
| 45 | Event Bus + State Architecture | Complete |
| 46 | Parallel Scheduler + Executor | Advanced hardened |
| 47 | OpenCode Bridge | Advanced hardened |
| 48 | OmniRoute Integration | Complete |
| 49 | Agent + Team Builder | Advanced hardened |
| 50 | Capability Authorization | Advanced hardened |
| 51 | Checkpoints + Resume | Complete |
| 52 | Context / Memory Economics | Complete |
| 53 | Persistent Sessions | Complete |
| 54 | Human-in-the-Loop | Complete |
| 55 | Durable Waiting + Scheduling | Complete |
| 56 | Intelligent Routing + Economics | Complete |
| 57 | Security Platform | Complete |
| 58 | Workspace / Worktree Lifecycle | Advanced hardened |
| 59 | Observability | Advanced hardened |
| 60 | Evaluation + Benchmarking | Advanced hardened |
| 61 | Continuous Improvement | Complete |
| 62 | Cross-Runtime / Cross-Harness | **Implemented; pending closure** |

## Phase 62 architecture

Phase 62 provides a common portable adapter contract for runtime, session, tool, model, event, capability, context, checkpoint, and artifact resources. `PortableAdapterRegistry` is deny-by-default and discovery-only; it grants no permissions.

`CrossRuntimeGateway` is the harness interoperability authority. It provides deterministic discovery, streaming capability filtering, preferred selection, health probes, bounded degradation/quarantine/recovery, project+harness session binding, explicit session migration, and safe fallback. Fallback is allowed only for retryable failures that occur before execution-start events. Routing evidence excludes request payloads and is bounded.

OpenCode, CLI, API, IDE, embedded, and agent harnesses can implement the same stable `HarnessAdapter` protocol. SI Core remains the only execution/governance authority; the gateway never silently changes capabilities, grants, execution state, or authorization.

## Cross-cutting invariants

Security decisions are fail-closed. Workspace, telemetry, evaluation, and improvement evidence are scoped and bounded. Human decisions and evaluation/improvement outcomes do not become capability grants. Web, TUI, CLI, and OpenCode remain clients of shared SI Core authority.

## Current position

**V4 Phases 44–62 are implemented; Phase 62 is pending final repository CI closure. Phase 63 — Ecosystem / Marketplace is next.**
