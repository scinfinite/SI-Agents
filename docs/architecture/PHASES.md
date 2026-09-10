# SI-Agents Implementation Phases

**Current status: v2.0 baseline plus Phases 19–21 implemented; Phase 21 awaits final CI verification.**

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
21. Agent Teams & Workflows — canonical teams, dependency DAG scheduling, bounded parallelism, context isolation/handoffs, retries, escalation, verification/evidence gates, cancellation, checkpoints, and auditable workflow events. **Implemented; final CI pending.**

## Release targets

- **Alpha:** phases 0–5 — achieved
- **Beta:** phases 6–9 — **complete**
- **v1.0:** phases 10–13 — **complete**
- **v1.5:** phases 14–15 — **complete**
- **v2.0:** phases 16–18 — **complete**
- **Post-v2 validation:** Phase 19 — **complete**
- **Post-v2 organization:** Phase 20 — **complete**
- **Post-v2 orchestration:** Phase 21 — **implemented; final CI pending**

## Verification rule

A phase is not considered complete merely because its files exist. Its acceptance criteria must be implemented, relevant tests must pass, CI must verify installation/build/lint/tests, and any CI failure discovered during completion must be fixed and rerun before the phase is declared complete.

## Phase 21 completion

Phase 21 adds the executable organization/team layer on top of Phase 20. `config/team-catalog.json` is the canonical source for declarative team/workflow definitions. `core/teams` provides typed team/task/execution/event contracts, a duplicate-safe registry, a stdlib-only loader, and a bounded dependency-aware executor.

The workflow engine schedules a dependency DAG deterministically, limits concurrency with team-level `max_parallelism`, supports explicit shared or isolated task context, uses `AgentResult.handoff` for portable handoffs, bounds retries, supports explicit escalation to declared team members, blocks downstream work after dependency failure, supports cooperative cancellation, and records ordered workflow events plus a final evidence checkpoint.

Team membership does not grant permissions or governance authority. Workers are injected into the engine and remain responsible for their existing permission checks; the existing governance/runtime layers remain authoritative. This preserves the separation established by Phases 13, 17, and 18.

The canonical `engineering-repair` workflow models debugger → developer → tester sequencing with evidence and verification gates. The acceptance suite covers dependency handoff, shared/isolated context, bounded parallelism, retry, escalation, verification/evidence gates, blocked downstream work, cancellation, cycle rejection, duplicate team rejection, and canonical catalog loading.

Verification evidence: final completion requires a successful main CI run covering distribution build, isolated wheel installation/import, Ruff, and the complete pytest suite. Phase 21 is not declared complete until that run passes.

Phase 21 intentionally does **not** claim external harness adapters, OpenCode/OmniRoute integration, Claude Code/Codex/Cline/Antigravity adapters, Termux/Codespace installers, model/quota routing, automatic persona generation, self-modifying promotion, or forced termination of arbitrary workers. Those remain later phases or deployment responsibilities. The detailed contract is documented in `docs/architecture/PHASE_21_AGENT_TEAMS_WORKFLOWS.md`.

## Phase 20 completion

Phase 20 establishes the first canonical organization layer. `config/agent-catalog.json` is the source of truth for 7 divisions and 12 agent definitions. `core/organization` provides typed definitions, lifecycle status, duplicate-safe registration, deterministic lookup/grouping, and selection by skills, capabilities, permissions, harness, environment, and status. The loader uses only the Python standard library. Implemented roles explicitly reference their existing Python workers; catalog-only roles remain declarative and are not presented as executable.

Catalog membership and selection do not grant permissions, invoke workers, spawn harnesses, or bypass governance. Runtime authorization remains with the existing permission and governance layers. This keeps organization data separate from execution authority and preserves the Phase 17/18 boundaries.

Verification evidence: the Phase 20 test suite covers canonical loading, catalog consistency, capability/permission selection, skill/harness/environment selection, duplicate rejection, and invalid status rejection. Final main CI run **#442** completed successfully on the Phase 20 mainline, verifying distribution build, isolated wheel installation/import, Ruff, and the full pytest suite. Final PR verification was also successful.

Phase 20 intentionally does **not** claim multi-agent orchestration, dynamic team execution, external harness adapters, OpenCode/OmniRoute integration, environment installers, automatic persona generation, or self-modifying agent promotion. Those remain separate future workstreams.

## Phase 19 completion

Phase 19 established the evidence-backed boundary for the next SI-Agents evolution. The audit confirmed that the v2.0 runtime boundary is executable and governed, while also identifying the missing user-facing cross-harness/environment layer. The `agents` package distribution gap was fixed; CI now installs the built wheel in an isolated environment and imports the agent/runtime APIs; and a dedicated integration test exercises a registered, enabled, governed runtime session through `RuntimeEngine` with streaming events.

The audit explicitly does **not** claim OpenCode, OmniRoute, Claude Code, Codex, Cline, Antigravity, Termux, Codespaces, unified setup/doctor CLI, agent divisions/teams, or cross-environment handoff as implemented. These remain future work and are documented in `docs/architecture/PHASE_19_REALITY_AUDIT.md`.

Verification evidence: PR #2 CI run #431 completed successfully with distribution build, isolated wheel installation/import, Ruff, and the full pytest suite. Main baseline CI run #428 and the v2 status synchronization PR #1 CI run #429 were also successful.

## Phase 18 completion

Phase 18 hardens the platform for production operation without overstating guarantees. Readiness checks are deterministic and fail closed on check failures; application-level resource limits bound accepted work; telemetry representations redact secret-like fields and bearer credentials; and a release gate requires evidence for tests, lint, build, security review, migration review, and rollback testing. CI now uses least-privilege contents-read permissions, cancels superseded runs, and bounds job duration. Production policy explicitly records compatibility, recovery, telemetry, and limit expectations.

Production hardening does not replace Phase 13 governance, does not turn the local executor into a security boundary, and does not claim that redaction prevents every possible secret leak. Infrastructure controls, operator procedures, backups, monitoring, incident response, and dependency management remain deployment responsibilities.

## Phase 17 completion

Phase 17 establishes a vendor-neutral runtime boundary. CLI, API, IDE, agent, embedded, and future harnesses use a typed invocation envelope with stable correlation, project identity, optional sessions, declared capabilities, normalized events, and structured errors. Harnesses are explicitly registered and disabled by default. The reference local adapter requires the existing Phase 13 governance decision before execution, so interoperability cannot bypass security, legal, cost, or data policy. A dependency-free conformance suite defines the minimum adapter contract; external harness SDKs are deliberately not added as hidden dependencies.

## Phase 16 completion

Phase 16 delivers a controlled learning pipeline in which evidence-backed proposals are evaluated through independent benchmark, regression, and safety gates before explicit approval. Application and rollback are externally supplied operations, so the learning engine cannot silently mutate code. Capability intelligence computes deterministic readiness signals from evidence, verification, benchmark, health, and confidence; missing signals are conservative, blocked capabilities score zero, and only validated capabilities are considered executable candidates. JSON persistence preserves proposal/evaluation evidence without adding a database dependency. Automatic code mutation, automatic capability promotion, automatic global promotion, and secret storage remain disabled by policy.

## Prior phase completion

Phases 10–15 delivered provenance-preserving open-source intelligence, evidence-gated pattern extraction, scoped engineering memory, executable security/legal/cost governance, typed model/provider intelligence, and governance-gated automation. Their existing completion documents remain authoritative for their respective acceptance criteria and verification evidence.
