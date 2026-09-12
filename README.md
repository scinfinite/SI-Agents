# SI-Agents

SI-Agents is the governed execution and agent platform for Project-SI. V4 is built around one authoritative SI Core exposed through Web, TUI, CLI, OpenCode, SDKs, workflows, and runtime/integration adapters.

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

- **Phases 44–66 are complete on `main`.**
- **Phase 66 — Advanced Web Control Plane** is fully implemented, audited, documented, merged through PR #79, and verified by final synchronized-tree mainline CI #1280 (`34699748468`).
- **Phase 63 — Ecosystem / Marketplace** is fully implemented, audited, documented, merged, and verified by final mainline CI #1198 (`34694418960`).
- **Phase 64 — SDK / Developer Platform** is fully implemented and merged through PR #78; its repository closure suite passed in CI #1239 (`34697885027`).
- **Phase 65 — Workflow + Automation** is fully implemented, audited, documented, and verified by final synchronized-tree CI #1249 (`34698187600`).
- **Phases 46, 47, 49, 50, 58, 59, and 60 passed dedicated advanced hardening.**

## Phase 66 — Advanced Web Control Plane

Phase 66 adds a secure, accessible, same-origin, dependency-free operational web client over the existing WebServer and versioned Control API. It provides dashboard/health, bounded live activity, workflow/run inspection, accessible topology/DAG views, evidence, identity-bound approvals, governed run-request controls, resources/settings, and bounded repository source/search/diff inspection.

The browser is a client of SI Core rather than a second authority. It inherits the established authentication/audit boundary, uses restrictive CSP and `nosniff`, rejects traversal and `.git` access, bounds source/diff/search workloads, uses timeout-bounded argument-vector Git inspection, and keeps streaming in the existing API while using bounded polling for dashboard refresh. No third-party runtime dependency, telemetry, inline script, inline style, or remote font is required.

Acceptance tests: `tests/unit/test_phase66_web_control.py` and `tests/unit/test_phase66_advanced_web.py`.

## Phase 65 — Workflow + Automation

Phase 65 adds a transport-neutral workflow state machine for versioned declarative DAGs, conditional branching, bounded fan-out and loops, delegation, human approval gates, durable waits, event/webhook/interval triggers, retries, runtime limits, cancellation, request-fingerprint-bound idempotency, durable JSON checkpoints, templates/import/export, restart validation, and reverse-order compensation.

Workflow adapters remain clients of SI Core and never create competing governance or execution authority. See `docs/architecture/PHASE_65_WORKFLOW_AUTOMATION.md` for the detailed contract and closure evidence.

## V4 roadmap

See `docs/architecture/SI_AGENTS_V4_PLAN.md` for the authoritative roadmap and `docs/architecture/PHASES.md` for phase evidence.

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
| 64 | SDK / Developer Platform | Complete |
| 65 | Workflow + Automation | Complete / 100% |
| 66 | Advanced Web Control Plane | **Complete / 100%** |
| 67 | Advanced TUI Control Center | **Next** |
| 68 | Advanced CLI Platform | Planned |
| 69 | npm Distribution + Setup | Planned |
| 70 | End-to-End Production Validation | Planned |
| 71 | Final Production Hardening | Planned |

## Engineering gate

A phase is not complete until implementation, unit/integration tests, security/adversarial tests, edge/failure tests, documentation synchronization, repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, and final exact-tree mainline CI are green. **Phase 66 satisfies this gate.**

## Current phase

**Phase 66 — Advanced Web Control Plane is 100% complete and closed on `main`. Phase 67 — Advanced TUI Control Center is next.**
