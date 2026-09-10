# SI-Agents Implementation Phases

**Current status: v2.0 track — Phases 1–18 complete and CI-verified.**

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

## Release targets

- **Alpha:** phases 0–5 — achieved
- **Beta:** phases 6–9 — **complete**
- **v1.0:** phases 10–13 — **complete**
- **v1.5:** phases 14–15 — **complete**
- **v2.0:** phases 16–18 — **complete**

## Verification rule

A phase is not considered complete merely because its files exist. Its acceptance criteria must be implemented, relevant tests must pass, CI must verify installation/build/lint/tests, and any CI failure discovered during completion must be fixed and rerun before the phase is declared complete.

## Phase 18 completion

Phase 18 hardens the platform for production operation without overstating guarantees. Readiness checks are deterministic and fail closed on check failures; application-level resource limits bound accepted work; telemetry representations redact secret-like fields and bearer credentials; and a release gate requires evidence for tests, lint, build, security review, migration review, and rollback testing. CI now uses least-privilege contents-read permissions, cancels superseded runs, and bounds job duration. Production policy explicitly records compatibility, recovery, telemetry, and limit expectations.

Production hardening does not replace Phase 13 governance, does not turn the local executor into a security boundary, and does not claim that redaction prevents every possible secret leak. Infrastructure controls, operator procedures, backups, monitoring, incident response, and dependency management remain deployment responsibilities.

## Phase 17 completion

Phase 17 establishes a vendor-neutral runtime boundary. CLI, API, IDE, agent, embedded, and future harnesses use a typed invocation envelope with stable correlation, project identity, optional sessions, declared capabilities, normalized events, and structured errors. Harnesses are explicitly registered and disabled by default. The reference local adapter requires the existing Phase 13 governance decision before execution, so interoperability cannot bypass security, legal, cost, or data policy. A dependency-free conformance suite defines the minimum adapter contract; external harness SDKs are deliberately not added as hidden dependencies.

## Phase 16 completion

Phase 16 delivers a controlled learning pipeline in which evidence-backed proposals are evaluated through independent benchmark, regression, and safety gates before explicit approval. Application and rollback are externally supplied operations, so the learning engine cannot silently mutate code. Capability intelligence computes deterministic readiness signals from evidence, verification, benchmark, health, and confidence; missing signals are conservative, blocked capabilities score zero, and only validated capabilities are considered executable candidates. JSON persistence preserves proposal/evaluation evidence without adding a database dependency. Automatic code mutation, automatic capability promotion, automatic global promotion, and secret storage remain disabled by policy.

## Prior phase completion

Phases 10–15 delivered provenance-preserving open-source intelligence, evidence-gated pattern extraction, scoped engineering memory, executable security/legal/cost governance, typed model/provider intelligence, and governance-gated automation. Their existing completion documents remain authoritative for their respective acceptance criteria and verification evidence.
