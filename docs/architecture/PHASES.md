# SI-Agents Implementation Phases

**Current status: v2.0 baseline plus Phases 19–21 complete; Phase 22 implementation in progress pending CI verification.**

1. Foundation — repository standards, architecture, policies, isolation, verification rules. **Complete.**
2. Control Plane — orchestration, task state, workflows, context, permissions, approvals, checkpoints. **Complete.**
3. Tool System — filesystem, terminal, Git, GitHub, web, code analysis, build/test tooling, containers, sandbox. **Complete.**
4. Engineering Brain — decomposition, planning, reasoning, hypotheses, root-cause analysis, trade-offs, uncertainty. **Complete.**
5. Developer/Debugger/Tester — first end-to-end engineering workflow and Alpha acceptance test. **Complete.**
6. Skills Engine — reusable, verifiable engineering procedures, lifecycle, selection, permissioned execution, and evidence. **Complete.**
7. Verification + Evidence — claims, evidence provenance, confidence, regression, red-team checks, production-readiness gates. **Complete.**
8. Technical Knowledge — universal programming model, languages, frameworks, ecosystems, standards. **Complete.**
9. Technology Discovery — detect, research, experiment, verify, and record unfamiliar technologies. **Complete.**
10. Open-Source Intelligence — repository archaeology, history, issues, PRs, releases, security, licenses, health. **Complete.**
11. Pattern Extraction — deterministic normalization, conservative extraction, independent validation, counterexamples, provenance, promotion, and matching. **Complete.**
12. Engineering Memory — task/project/global memory, evidence-gated promotion, scoped retrieval, lifecycle, supersession, and auditable persistence. **Complete.**
13. Security + Legal + Cost — executable governance gates, free-first cost controls, data classification/egress, provenance/legal review, risk classification, approvals, and audit evidence. **Complete.**
14. Model/Provider Intelligence — capability, quota, cost, latency, reliability, fallback, circuit breakers. **Complete.**
15. Automation — scheduled research, monitoring, maintenance, testing, reporting, retries, idempotency, lifecycle, persistence, and governance-gated execution. **Complete.**
16. Controlled Self-Improvement + Capability Intelligence — evidence-backed proposals, benchmark/regression/safety gates, explicit approval, rollback, capability readiness intelligence, conservative unknown handling, and auditable persistence. **Complete.**
17. Harness & Runtime Interoperability — transport-neutral invocation, capability negotiation, normalized events/errors, project sessions, explicit harness registration, governed local adapter, and conformance tests. **Complete.**
18. Production Hardening — deterministic readiness, explicit resource limits, telemetry redaction, evidence-based release gates, migration/rollback requirements, and CI hardening. **Complete.**
19. v2.0 Reality Audit — executable baseline audit, runtime E2E acceptance, distribution correctness, isolated wheel verification, documentation/roadmap consistency, and evidence-backed future-boundary definition. **Complete.**
20. Agent Organization & Catalog — canonical divisions, typed agent definitions, declarative selection, lifecycle status, implementation references, and organization validation. **Complete.**
21. Agent Teams & Workflows — canonical teams, dependency DAG scheduling, bounded parallelism, context isolation/handoffs, retries, escalation, verification/evidence gates, cancellation, checkpoints, and auditable workflow events. **Complete.**
22. Universal Harness Integration — versioned language-neutral wire contract, structural callback bridge, adapter discovery, organization deployment manifests, and conformance coverage. **In progress — implementation complete, CI pending.**

## Release targets

- **Alpha:** phases 0–5 — achieved
- **Beta:** phases 6–9 — **complete**
- **v1.0:** phases 10–13 — **complete**
- **v1.5:** phases 14–15 — **complete**
- **v2.0:** phases 16–18 — **complete**
- **Post-v2 validation:** Phase 19 — **complete**
- **Post-v2 organization:** Phase 20 — **complete**
- **Post-v2 orchestration:** Phase 21 — **complete**
- **Post-v2 interoperability:** Phase 22 — **in progress**

## Verification rule

A phase is not considered complete merely because its files exist. Its acceptance criteria must be implemented, relevant tests must pass, CI must verify installation/build/lint/tests, and any CI failure discovered during completion must be fixed and rerun before the phase is declared complete.

## Phase 22 implementation

Phase 22 extends the Phase 17 runtime boundary without coupling the core to a vendor harness. `core/runtime/wire.py` defines the versioned `si.runtime.v1` JSON-compatible envelope; `core/runtime/bridge.py` provides a callback-based adapter bridge and normalized metadata discovery; and `core/runtime/deployment.py` provides a deterministic organization exposure manifest for Phase 20/21 agents, teams, skills, permissions, and capabilities.

Deployment manifests are descriptive only. They do not enable harnesses, grant permissions, invoke workers, bypass governance, or install configuration. The existing deny-by-default harness registry, session isolation, capability checks, and governance decision remain authoritative.

Phase 22 deliberately stops before vendor-specific integration. OpenCode, Codex, Claude Code, Cline, Antigravity, OmniRoute, Termux, Codespaces, and installation/configuration workflows remain subsequent phases or deployment responsibilities.

## Phase 21 completion

Phase 21 adds the executable organization/team layer on top of Phase 20. `config/team-catalog.json` is the canonical source for declarative team/workflow definitions. `core/teams` provides typed team/task/execution/event contracts, a duplicate-safe registry, a stdlib-only loader, and a bounded dependency-aware executor.

The workflow engine schedules a dependency DAG deterministically, limits concurrency with team-level `max_parallelism`, supports explicit shared or isolated task context, uses `AgentResult.handoff` for portable handoffs, bounds retries, supports explicit escalation to declared team members, blocks downstream work after dependency failure, supports cooperative cancellation, and records ordered workflow events plus a final evidence checkpoint.

Team membership does not grant permissions or governance authority. Workers are injected into the engine and remain responsible for their existing permission checks; the existing governance/runtime layers remain authoritative. This preserves the separation established by Phases 13, 17, and 18.

The canonical `engineering-repair` workflow models debugger → developer → tester sequencing with evidence and verification gates. The acceptance suite covers dependency handoff, shared/isolated context, bounded parallelism, retry, escalation, verification/evidence gates, blocked downstream work, cancellation, cycle rejection, duplicate team rejection, and canonical catalog loading.

Final verification evidence: CI run **#450** passed distribution build, isolated wheel installation/import, Ruff, and the complete pytest suite, with **284 tests passing**. The final completion fixes included enforcing isolated-context non-publication and keeping verification gates active during escalation.

Phase 21 intentionally does **not** claim external harness adapters, OpenCode/OmniRoute integration, Claude Code/Codex/Cline/Antigravity adapters, Termux/Codespace installers, model/quota routing, automatic persona generation, self-modifying promotion, or forced termination of arbitrary workers. Those remain later phases or deployment responsibilities. The detailed contract is documented in `docs/architecture/PHASE_21_AGENT_TEAMS_WORKFLOWS.md`.
