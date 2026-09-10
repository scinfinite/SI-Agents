# SI-Agents Implementation Phases

**Current status: Beta — Phases 1–7 complete and CI-verified. Phase 8 is next.**

1. Foundation — repository standards, architecture, policies, isolation, verification rules. **Complete.**
2. Control Plane — orchestration, task state, workflows, context, permissions, approvals, checkpoints. **Complete.**
3. Tool System — filesystem, terminal, Git, GitHub, web, code analysis, build/test tooling, containers, sandbox. **Complete.**
4. Engineering Brain — decomposition, planning, reasoning, hypotheses, root-cause analysis, trade-offs, uncertainty. **Complete.**
5. Developer/Debugger/Tester — first end-to-end engineering workflow and Alpha acceptance test. **Complete.**
6. Skills Engine — reusable, verifiable engineering procedures, lifecycle, selection, permissioned execution, and evidence. **Complete.**
7. Verification + Evidence — claims, evidence provenance, confidence, regression, red-team checks, production-readiness gates. **Complete.**
8. Technical Knowledge — universal programming model, languages, frameworks, ecosystems, standards.
9. Technology Discovery — detect, research, experiment, verify, and record unfamiliar technologies.
10. Open-Source Intelligence — repository archaeology, history, issues, PRs, releases, security, licenses, health.
11. Pattern Extraction — generalize and independently validate reusable engineering patterns.
12. Engineering Memory — task/project/global memory with controlled promotion.
13. Security + Legal + Cost — governance gates, free-first routing, data rights, security and compliance.
14. Model/Provider Intelligence — capability, quota, cost, latency, reliability, fallback, circuit breakers.
15. Automation — scheduled research, monitoring, maintenance, testing, and reporting.
16. Controlled Self-Improvement + Capability Intelligence — evidence-backed learning, benchmarks, regression, and validated/experimental/unknown capability states.
17. Harness & Runtime Interoperability — OpenCode, Codex, Claude Code, Cline, Termux, Codespaces, terminal, and future harness adapters over one SI-Agents core.
18. Production Hardening — end-to-end reliability, security, performance, compatibility, migration, observability, and release readiness.

## Release targets

- **Alpha:** phases 0–5 — achieved
- **Beta:** phases 6–9 — **in progress; Phases 6–7 achieved**
- **v1.0:** phases 10–13
- **v1.5:** phases 14–15
- **v2.0:** phases 16–18

## Verification rule

A phase is not considered complete merely because its files exist. Its acceptance criteria must be implemented, relevant tests must pass, CI must verify installation/build/lint/tests, and any CI failure discovered during completion must be fixed and rerun before the phase is declared complete.
