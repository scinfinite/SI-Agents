# SI-Agents Implementation Phases

**Current status: v1.0 track — Phases 1–10 complete and CI-verified. Phase 11 is next.**

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
- **Beta:** phases 6–9 — **complete**
- **v1.0:** phases 10–13 — **Phase 10 complete; phases 11–13 remain**
- **v1.5:** phases 14–15
- **v2.0:** phases 16–18

## Verification rule

A phase is not considered complete merely because its files exist. Its acceptance criteria must be implemented, relevant tests must pass, CI must verify installation/build/lint/tests, and any CI failure discovered during completion must be fixed and rerun before the phase is declared complete.

## Phase 10 completion

Phase 10 delivered a provenance-preserving open-source intelligence layer covering repository metadata, archaeology/history, issues, pull requests, releases, security advisories, conservative license assessment, project health, freshness, and a read-only provider contract. External repository content remains untrusted research input and is never treated as system policy. Unknown license/health signals remain explicitly uncertain. Final CI evidence is recorded in `docs/architecture/PHASE_10_OPEN_SOURCE_INTELLIGENCE.md` after the final workflow completes.
