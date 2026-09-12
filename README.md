# SI-Agents

SI-Agents is the governed execution and agent platform for Project-SI. V4 is being built as one authoritative SI Core exposed through Web, TUI, CLI, OpenCode, and runtime/integration adapters.

## V4 product direction

```text
User prompt → OpenCode → SI Core → Scheduler/Orchestrator
→ Agents/Teams/Workflows → Authorization → OmniRoute
→ Models/Providers/APIs → Results/Evidence → SI Core
→ Observability → Evaluation → Continuous Improvement
→ Release Gates / Canaries / Rollback → OpenCode / Web / TUI / CLI
```

OpenCode is a primary user-facing harness. OmniRoute is the model/provider/API routing layer. SI Core remains authoritative for execution state, orchestration, governance, evidence, lifecycle, persistence, recovery, workspace lifecycle, observability, evaluation, and continuous-improvement governance.

## Current V4 status

- **Phases 44–61 are complete on `main`.**
- **Phases 46, 47, 49, 50, 58, 59, and 60 passed dedicated advanced hardening.**
- **Phase 61 — Continuous Improvement:** merged PR #75; PR CI #1157 (`34692165853`) green.
- Phase 58–60 hardening PR #74 passed PR CI #1143 (`34691131729`) and final synchronized-tree mainline CI #1144 (`34691176676`).

## Phase 61 — Continuous Improvement

Phase 61 converts evaluation evidence into bounded, explainable improvement proposals across agents, teams, models, routing, and workflows. It provides failure clustering, regression signals, recommendation risk/confidence, deterministic weighted experiments, fail-closed canary gates, human approval binding for consequential changes, rollback plans, and tamper-evident improvement history.

The authority rejects secret-like content before persistence and deliberately does **not** mutate runtime state directly. Approved execution remains under SI Core scheduler, capability authorization, deployment/workspace, and runtime authorities.

## V4 roadmap

The full detailed roadmap is maintained in `docs/architecture/SI_AGENTS_V4_PLAN.md`.

| Phase | Name | Status |
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
| 62 | Cross-Runtime / Cross-Harness | Next |
| 63 | Ecosystem / Marketplace | Planned |
| 64 | SDK / Developer Platform | Planned |
| 65 | Workflow + Automation | Planned |
| 66 | Advanced Web Control Plane | Planned |
| 67 | Advanced TUI Control Center | Planned |
| 68 | Advanced CLI Platform | Planned |
| 69 | npm Distribution + Setup | Planned |
| 70 | End-to-End Production Validation | Planned |
| 71 | Final Production Hardening | Planned |

## Engineering gate

A phase is not complete until implementation, unit/integration tests, security/adversarial tests, edge/failure tests, documentation synchronization, repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, and final exact-tree mainline CI are green. After every phase and cross-phase hardening audit, README, docs/index, architecture/index, V4 plan, phase index, phase records, and affected cross-cutting documents must be synchronized.

## Next phase

**Phase 62 — Cross-Runtime / Cross-Harness**.
