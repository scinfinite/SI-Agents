# SI-Agents

SI-Agents is the governed execution and agent platform for Project-SI. V4 is being built as one authoritative SI Core exposed through Web, TUI, CLI, OpenCode, and runtime/integration adapters.

## V4 product direction

```text
User prompt → OpenCode → SI Core → Scheduler/Orchestrator
→ Agents/Teams/Workflows → Authorization → OmniRoute
→ Models/Providers/APIs → Results/Evidence → SI Core
→ OpenCode / Web / TUI / CLI
```

OpenCode is a primary user-facing harness. OmniRoute is the model/provider/API routing layer. SI Core remains authoritative for execution state, orchestration, governance, evidence, lifecycle, persistence, recovery, workspace lifecycle, observability, and evaluation.

## Current V4 status

- **Phases 44–60 are complete at the required advanced-hardening level on main.**
- **Phase 61 — Continuous Improvement is next.**
- **Phases 46, 47, 49, 50, 58, 59, and 60 have passed dedicated advanced hardening.**
- Phase 58–60 hardening PR #74 passed PR CI #1143 (`34691131729`) and final synchronized-tree mainline CI #1144 (`34691176676`).
- The final mainline gate passed distribution/wheel verification, repository audit, integration verification, Ruff, and full pytest.

## Phase 58 — Workspace / Worktree Lifecycle — advanced hardened

The workspace authority provides tenant/project isolation, optimistic revisions, bounded lease locks, directory and Git-worktree materialization, branch lifecycle, dirty/conflict inspection, deterministic diffs and merge preparation, snapshots and diff artifacts, approved resume, recovery/cleanup, path and symlink defenses, tamper-evident lifecycle evidence, and bounded garbage-collection discovery. Advanced hardening adds adversarial event-chain tamper detection and sensitive-operation authorization callback coverage.

## Phase 59 — Observability — advanced hardened

The observability authority provides bounded structured logs/events/metrics/spans, shared security-scanner secret detection and redaction, correlation/causation, trace timelines, live-feed retention, percentile metrics, operator health, JSONL export, tenant/project filtering, and SHA-256 integrity evidence. Advanced hardening verifies tampering beyond the first query page and tightens resource/severity contracts.

## Phase 60 — Evaluation + Benchmarking — advanced hardened

The evaluation authority provides deterministic golden cases, multi-mode scoring, weighted dimensions, reliability/security/latency/cost measurements, failure classification, benchmark history, regression detection, human review, deterministic weighted experiments, cryptographic report digests, and release gates. Advanced hardening makes cost/latency budgets enforceable, rejects secret-bearing evaluator outputs/metadata/review rationale, verifies persisted evidence integrity, tightens experiment inputs, and fails closed on empty reports.

## Phase 56 — Intelligent Routing + Economics

Phase 56 adds deterministic SI-side routing intelligence while preserving OmniRoute as the model/provider/API routing boundary.

Covered contracts:

- explicit task complexity and capability requirements;
- model/agent capability, context-window, streaming, structured-output, vision, coding, reasoning, and tool matching;
- quality, reliability-history, latency, cost, and preference scoring;
- quota, provider/model enablement, and circuit-breaker gating;
- preferred providers/models and deterministic tie-breaking;
- budget reservations and settlement with fail-closed limits;
- cost and retry forecasting;
- bounded transient/rate-limit fallback;
- escalation/downgrade controls;
- non-secret route evidence and failure classification;
- health outcome recording and recovery probes.

## Phase 55 — Durable Waiting + Scheduling

Phase 55 adds durable SQLite-backed SI Core waiting and scheduling with an explicit `waiting → ready → claimed → completed` lifecycle.

Covered contracts include timer/delayed waits, recurrence/cron, approval/human/dependency/resource/external wake-up, deadlines/expiry, restart recovery, starvation resistance, optimistic revisions, bounded queue/payload limits, secret rejection, identity/project isolation, and Control API lifecycle routes. Claims never grant credentials, capabilities, provider authorization, or identity.

## Previously advanced-hardened phases

Phases 46, 47, 49, and 50 remain advanced-hardened under hardening CI #984 (`34671292491`).

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
| 61 | Continuous Improvement | Next |
| 62 | Cross-Runtime / Cross-Harness | Planned |
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
