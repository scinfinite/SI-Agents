# SI-Agents Implementation Phases

**Current status: v1.5 track — Phases 1–14 complete and CI-verified. Phase 15 is next.**

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
15. Automation — scheduled research, monitoring, maintenance, testing, and reporting.
16. Controlled Self-Improvement + Capability Intelligence — evidence-backed learning, benchmarks, regression, and validated/experimental/unknown capability states.
17. Harness & Runtime Interoperability — OpenCode, Codex, Claude Code, Cline, Termux, Codespaces, terminal, and future harness adapters over one SI-Agents core.
18. Production Hardening — end-to-end reliability, security, performance, compatibility, migration, observability, and release readiness.

## Release targets

- **Alpha:** phases 0–5 — achieved
- **Beta:** phases 6–9 — **complete**
- **v1.0:** phases 10–13 — **complete**
- **v1.5:** phases 14–15 — **Phase 14 complete; Phase 15 next**
- **v2.0:** phases 16–18

## Verification rule

A phase is not considered complete merely because its files exist. Its acceptance criteria must be implemented, relevant tests must pass, CI must verify installation/build/lint/tests, and any CI failure discovered during completion must be fixed and rerun before the phase is declared complete.

## Phase 10 completion

Phase 10 delivered a provenance-preserving open-source intelligence layer covering repository metadata, archaeology/history, issues, pull requests, releases, security advisories, conservative license assessment, project health, freshness, and a read-only provider contract. External repository content remains untrusted research input and is never treated as system policy. Unknown license/health signals remain explicitly uncertain. Final CI evidence is recorded in `docs/architecture/PHASE_10_OPEN_SOURCE_INTELLIGENCE.md` after the final workflow completes.

## Phase 11 completion

Phase 11 delivers deterministic normalization of engineering observations, conservative candidate extraction, independent verified-evidence validation, explicit counterexample handling, provenance retention, evidence-gated registry promotion/versioning, and context matching. A pattern match is a ranking signal, not proof. Promotion remains fail-closed until the documented evidence and confidence criteria pass. Final CI evidence is recorded by the repository workflow on the completed Phase 11 head.

## Phase 12 completion

Phase 12 delivers task/project/global engineering memory with mandatory provenance, verified-evidence and confidence gates, fail-closed one-step promotion, deterministic scope-aware retrieval, expiration, explicit supersession/versioning, and dependency-free JSON persistence. Memory is data rather than policy and cannot override security, legal, cost, permission, or verification controls. Final CI evidence is recorded after the completed Phase 12 head passes the repository workflow.

## Phase 13 completion

Phase 13 delivers executable governance for security, legal/provenance, cost, data egress, permissions, and risk. Governance requests receive deterministic allow/deny/approval-required decisions; credential-bearing external egress is denied, sensitive/confidential egress and paid resources are approval-gated, publication requires provenance, high-risk destructive operations require approval, and effective risk is derived conservatively. Audit records retain decision evidence without request payloads. Final CI evidence is required on the completed Phase 13 head.

## Phase 14 completion

Phase 14 delivers typed model/provider intelligence with explicit provider/model registration, hard capability matching, deterministic cost and latency constraints, free-first ranking, quota freshness tracking, bounded health observations, provider circuit breakers, and constraint-preserving fallback. The router is a decision layer and never executes provider calls or bypasses Phase 13 governance. Unknown capabilities/cost are not fabricated as supported/free, and credentials are excluded from provider metadata. Final CI evidence is required on the completed Phase 14 head.
