# SI-Agents V4 Plan

## Authority

SI-Agents V4 is built around one authoritative SI Core. Web, TUI, CLI, npm, OpenCode, runtime adapters, schedulers, agents, teams, workflows, SDKs, and integrations are clients/adapters, not competing state authorities.

```text
User → OpenCode / Web / TUI / CLI / npm / SDK → SI Core / Control API
     → Capacity → Scheduler / Orchestrator → Tasks / Agents / Teams / Workflows
     → Capability Authorization → OmniRoute → Models / Providers / APIs
     → Results / Artifacts / Evidence → SI Core
     → Observability → Evaluation → Continuous Improvement
     → Cross-Runtime → Ecosystem / Marketplace → Release Gates / Canaries / Rollback → Clients
```

OmniRoute owns model/provider/API routing. SI Core owns execution, orchestration, governance, evidence, lifecycle, persistence, recovery, waiting, workspaces, observability, evaluation, and improvement governance.

## Current position

V3 is closed. V4 has completed Phases **44–70**. Phases **46, 47, 49, 50, 58, 59, and 60** were advanced-hardened. **Phase 71 — Final Production Hardening is implemented and awaiting final mainline CI closure.**

### Phase 70 — End-to-End Production Validation

**Complete / 100%.** Phase 70 validates OpenCode → SI RuntimeEngine → OmniRoute → model/provider boundary → SI → OpenCode using deterministic CI-safe boundary transports. It adds direct end-to-end acceptance coverage plus governance-denial, session-isolation, model-fallback, and cancellation-boundary checks. Existing runtime, OpenCode, OmniRoute, Web/TUI/CLI, SDK, wheel, npm, repository-audit, compileall, Ruff, and full pytest gates remain mandatory and green.

Implementation/test coverage: `tests/integration/test_phase70_production_path.py`.

Detailed acceptance record: `docs/architecture/phases/PHASE_70_END_TO_END_PRODUCTION_VALIDATION.md`.

## Phase 71 — Final Production Hardening

**Implementation complete / final verification pending.** The final hardening pass adds a bounded thread-safe invocation ledger at the authoritative RuntimeEngine boundary. Lifecycle entries are keyed by `(harness_id, request_id)`, terminal responses are replayable, request-ID payload confusion fails closed, concurrent duplicate requests cannot execute a capability twice, cancellation is terminal, and request-state retention is bounded.

Implementation:

- `core/runtime/lifecycle.py`
- `core/runtime/engine.py`
- `core/runtime/__init__.py`

Acceptance coverage:

- `tests/integration/test_phase71_final_hardening.py`

Detailed contract: `docs/architecture/phases/PHASE_71_FINAL_PRODUCTION_HARDENING.md`.

## Closure gate

A phase is closed only after implementation, unit/integration tests, adversarial/security tests, edge/failure tests, documentation synchronization, repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, SDK verification, merge, and final exact-tree mainline CI are green. Phase 69 additionally requires npm package-content, version/license, and launcher smoke verification. Phase 70 additionally requires deterministic end-to-end production-path coverage and explicit failure-containment checks. Phase 71 additionally requires lifecycle/idempotency/concurrency/cancellation hardening coverage and post-merge verification on the exact final mainline tree.
