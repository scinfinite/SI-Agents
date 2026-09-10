# SI-Agents Implementation Phases

**Current status: v1.5 track — Phases 1–15 complete and CI-verified. Phase 16 is next.**

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
16. Controlled Self-Improvement + Capability Intelligence — evidence-backed learning, benchmarks, regression, and validated/experimental/unknown capability states.
17. Harness & Runtime Interoperability — OpenCode, Codex, Claude Code, Cline, Termux, Codespaces, terminal, and future harness adapters over one SI-Agents core.
18. Production Hardening — end-to-end reliability, security, performance, compatibility, migration, observability, and release readiness.

## Release targets

- **Alpha:** phases 0–5 — achieved
- **Beta:** phases 6–9 — **complete**
- **v1.0:** phases 10–13 — **complete**
- **v1.5:** phases 14–15 — **complete**
- **v2.0:** phases 16–18

## Verification rule

A phase is not considered complete merely because its files exist. Its acceptance criteria must be implemented, relevant tests must pass, CI must verify installation/build/lint/tests, and any CI failure discovered during completion must be fixed and rerun before the phase is declared complete.

## Phase 15 completion

Phase 15 delivers dependency-free automation primitives for one-shot and recurring schedules, deterministic due-job selection and catch-up, explicit lifecycle controls, registered-action execution, conditional triggers, bounded retries with exponential backoff, idempotency, governance gating, run history, and JSON persistence. Automation is not a policy authority: every action remains subject to existing governance and permission boundaries. No hosted scheduler, paid queue, credential store, or arbitrary shell execution was introduced. Final CI evidence is required on the completed Phase 15 head.

## Prior phase completion

Phases 10–14 delivered provenance-preserving open-source intelligence, evidence-gated pattern extraction, scoped engineering memory, executable security/legal/cost governance, and typed model/provider intelligence. Their existing completion documents remain authoritative for their respective acceptance criteria and verification evidence.
