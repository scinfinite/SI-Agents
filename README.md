# SI-Agents

SI-Agents is the governed execution and agent platform for Project-SI. V4 is built around one authoritative SI Core exposed through Web, TUI, CLI, OpenCode, SDKs, and runtime/integration adapters.

## V4 product direction

```text
User prompt → OpenCode / Web / TUI / CLI / SDK → SI Core → Scheduler/Orchestrator
→ Agents/Teams/Workflows → Authorization → OmniRoute
→ Models/Providers/APIs → Results/Evidence → SI Core
→ Observability → Evaluation → Continuous Improvement
→ Cross-Runtime → Ecosystem / Marketplace → Release Gates / Canaries / Rollback → Clients
```

OpenCode is a primary user-facing harness. OmniRoute is the model/provider/API routing layer. SI Core remains authoritative for execution state, orchestration, governance, evidence, lifecycle, persistence, recovery, workspace lifecycle, observability, evaluation, continuous improvement, and cross-runtime governance.

## Current V4 status

- **Phases 44–63 are complete on `main`.**
- **Phase 62 — Cross-Runtime / Cross-Harness is fully implemented, audited, documented, merged, and verified by mainline CI.**
- **Phase 63 — Ecosystem / Marketplace is fully implemented, audited, documented, merged, and verified by final mainline CI #1198 (`34694418960`).**
- **Phase 64 — SDK / Developer Platform is in implementation pending final exact-tree mainline CI.**
- **Phases 46, 47, 49, 50, 58, 59, and 60 passed dedicated advanced hardening.**

## Phase 64 — SDK / Developer Platform

Phase 64 adds typed Python and TypeScript SDKs over the versioned Control API, stable errors, optional bearer authentication, header-bound identity, filter-bound cursor pagination, idempotent run creation, bounded concurrency, SSE/WebSocket event transports, explicit subscriptions, signed webhook delivery primitives, OpenAPI updates, examples, and a dedicated SDK CI gate.

SDKs remain clients/adapters. They do not create execution or governance authority outside SI Core.

## V4 roadmap

See `docs/architecture/SI_AGENTS_V4_PLAN.md` for the authoritative roadmap and `docs/architecture/PHASE_64_SDK_DEVELOPER_PLATFORM.md` for the current Phase 64 contract.

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
| 62 | Cross-Runtime / Cross-Harness | Complete |
| 63 | Ecosystem / Marketplace | Complete |
| 64 | SDK / Developer Platform | In implementation |
| 65 | Workflow + Automation | Planned |
| 66 | Advanced Web Control Plane | Planned |
| 67 | Advanced TUI Control Center | Planned |
| 68 | Advanced CLI Platform | Planned |
| 69 | npm Distribution + Setup | Planned |
| 70 | End-to-End Production Validation | Planned |
| 71 | Final Production Hardening | Planned |

## Engineering gate

A phase is not complete until implementation, unit/integration tests, security/adversarial tests, edge/failure tests, documentation synchronization, repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, and final exact-tree mainline CI are green.

## Current phase

**Phase 64 — SDK / Developer Platform.**
