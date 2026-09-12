# SI-Agents

SI-Agents is the governed execution and agent platform for Project-SI. V4 is built around one authoritative SI Core exposed through Web, TUI, CLI, OpenCode, and runtime/integration adapters.

## V4 product direction

```text
User prompt → OpenCode / Web / TUI / CLI → SI Core → Scheduler/Orchestrator
→ Agents/Teams/Workflows → Authorization → OmniRoute
→ Models/Providers/APIs → Results/Evidence → SI Core
→ Observability → Evaluation → Continuous Improvement
→ Cross-Runtime → Release Gates / Canaries / Rollback → Clients
```

OpenCode is a primary user-facing harness. OmniRoute is the model/provider/API routing layer. SI Core remains authoritative for execution state, orchestration, governance, evidence, lifecycle, persistence, recovery, workspace lifecycle, observability, evaluation, continuous improvement, and cross-runtime governance.

## Current V4 status

- **Phases 44–62 are complete on `main`.**
- **Phase 62 — Cross-Runtime / Cross-Harness is fully implemented, audited, documented, merged, and verified by mainline CI.**
- **Phases 46, 47, 49, 50, 58, 59, and 60 passed dedicated advanced hardening.**
- Phase 61 merged as PR #75 / CI #1157 (`34692165853`).
- Phase 62 merged as PR #76 / PR CI #1166 (`34692621358`).
- Phase 62 mainline CI #1180 (`34693460152`) passed the repository closure suite on the integration-marker correction.

## Phase 62 — Cross-Runtime / Cross-Harness

Phase 62 adds portable adapter contracts for runtime, session, tool, model, event, capability, context, checkpoint, and artifact resources. The cross-runtime gateway provides deterministic harness discovery, capability filtering, health probing, bounded quarantine/recovery, preferred selection, project+harness session isolation, explicit migration, and safe pre-start fallback.

Fallback is prohibited after execution-start signals. Routing decisions exclude request payloads. Registration/discovery never grants permissions, and the gateway never becomes an execution authority. OpenCode remains a supported harness rather than the definition of the runtime protocol.

## V4 roadmap

See `docs/architecture/SI_AGENTS_V4_PLAN.md` for the authoritative roadmap and `docs/architecture/PHASE_62_CROSS_RUNTIME_CROSS_HARNESS.md` for the Phase 62 contract.

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
| 63 | Ecosystem / Marketplace | Next |
| 64 | SDK / Developer Platform | Planned |
| 65 | Workflow + Automation | Planned |
| 66 | Advanced Web Control Plane | Planned |
| 67 | Advanced TUI Control Center | Planned |
| 68 | Advanced CLI Platform | Planned |
| 69 | npm Distribution + Setup | Planned |
| 70 | End-to-End Production Validation | Planned |
| 71 | Final Production Hardening | Planned |

## Engineering gate

A phase is not complete until implementation, unit/integration tests, security/adversarial tests, edge/failure tests, documentation synchronization, repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, and final exact-tree mainline CI are green.

## Next phase

**Phase 63 — Ecosystem / Marketplace.**
