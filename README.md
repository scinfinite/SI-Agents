# SI-Agents

SI-Agents is the governed execution and agent platform for Project-SI. V4 is built around one authoritative SI Core exposed through Web, TUI, CLI, OpenCode, and runtime/integration adapters.

## V4 product direction

```text
User prompt → OpenCode / Web / TUI / CLI → SI Core → Scheduler/Orchestrator
→ Agents/Teams/Workflows → Authorization → OmniRoute
→ Models/Providers/APIs → Results/Evidence → SI Core
→ Observability → Evaluation → Continuous Improvement
→ Cross-Runtime → Ecosystem / Marketplace → Release Gates / Canaries / Rollback → Clients
```

OpenCode is a primary user-facing harness. OmniRoute is the model/provider/API routing layer. SI Core remains authoritative for execution state, orchestration, governance, evidence, lifecycle, persistence, recovery, workspace lifecycle, observability, evaluation, continuous improvement, and cross-runtime governance.

## Current V4 status

- **Phases 44–63 are complete on `main`.**
- **Phase 62 — Cross-Runtime / Cross-Harness is fully implemented, audited, documented, merged, and verified by mainline CI.**
- **Phase 63 — Ecosystem / Marketplace is fully implemented, audited, documented, merged, and verified by its final mainline CI closure gate.**
- **Phases 46, 47, 49, 50, 58, 59, and 60 passed dedicated advanced hardening.**
- Phase 61 merged as PR #75 / CI #1157 (`34692165853`).
- Phase 62 merged as PR #76 / final mainline CI #1186 (`34693756693`).
- Phase 63 merged as PR #77 / PR CI #1189 (`34694186010`) and final synchronized-tree mainline CI is the authoritative closure gate.

## Phase 63 — Ecosystem / Marketplace

Phase 63 provides strict versioned marketplace manifests, dependency and compatibility declarations, explicit permission declarations, provenance/trust, exact manifest identity, deterministic package/template registries, governed install/update/uninstall/rollback lifecycle, bounded history, and drift detection.

Marketplace lifecycle is metadata/state management only. Installation never grants execution authority; untrusted packages require explicit governance, and governance approval is bound to the exact manifest digest. SI Core remains authoritative for authorization and execution.

## V4 roadmap

See `docs/architecture/SI_AGENTS_V4_PLAN.md` for the authoritative roadmap and `docs/architecture/PHASE_63_ECOSYSTEM_MARKETPLACE.md` for the Phase 63 contract.

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
| 64 | SDK / Developer Platform | Next |
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

**Phase 64 — SDK / Developer Platform.**
