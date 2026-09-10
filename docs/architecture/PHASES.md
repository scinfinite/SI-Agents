# SI-Agents Implementation Phases

**Current status: v2.0 baseline plus Phases 19–28 complete; Phase 29 reopened for full Agency Agents parity.**

> This file is the authoritative current implementation/status record. `docs/architecture/SI_AGENTS_V3.md` is the forward-looking roadmap, but Phase 30 is blocked until the reopened Phase 29 gate passes. `docs/README.md` and `docs/architecture/README.md` are the documentation navigation indexes.

## Completed phases

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
22. Universal Harness Integration — versioned language-neutral wire contract, structural callback bridge, adapter discovery, organization deployment manifests, and conformance coverage. **Complete.**
23. OpenCode Integration — headless-server adapter, session continuity, normalized messages/events, cancellation, safe authentication handling, and distribution/CI verification. **Complete.**
24. OmniRoute Integration — OpenAI-compatible gateway transport, deterministic model discovery, secure credential handling, fail-closed health/failure classification, correlation/session forwarding, and a governed delegation boundary that keeps provider/model routing authoritative in OmniRoute. **Complete.**
25. Termux Runtime — environment detection, readiness checks, OpenCode/OmniRoute health integration, read-only doctor, sanitized reports, conservative package planning, and workspace validation. **Complete.**
26. GitHub Codespaces Runtime — Codespaces detection, toolchain/workspace readiness, OpenCode/GitHub CLI/OmniRoute requirements, read-only doctor, and sanitized reports. **Complete.**
27. `si` CLI + Easy Setup — user-facing doctor/status/catalog/team/setup/update/run commands, non-secret configuration, explicit mutation gates, OpenCode/OmniRoute configuration, governed team execution, packaged canonical catalogs, and wheel-level CLI verification. **Complete.**
28. Cross-environment & Handoff — portable `si.handoff.v1` state, SHA-256 integrity, secret-like field rejection, sanitized/canonical repository identity, explicit Termux↔Codespaces validation, resumable workflow context, atomic storage, and CLI handoff commands. **Complete and CI-verified.**
29. Complete Agent Persona Corpus & Definition System — reopened. Persona parser/compiler/registry machinery exists, but the canonical corpus is being expanded from seven personas to parity with the pinned Agency Agents source-agent snapshot. **Audit in progress; not complete.**

## Release targets

- **Alpha:** phases 0–5 — achieved
- **Beta:** phases 6–9 — complete
- **v1.0:** phases 10–13 — complete
- **v1.5:** phases 14–15 — complete
- **v2.0:** phases 16–18 — complete
- **Post-v2 validation:** Phase 19 — complete
- **Post-v2 organization:** Phase 20 — complete
- **Post-v2 orchestration:** Phase 21 — complete
- **Post-v2 interoperability:** Phase 22 — complete
- **Post-v2 OpenCode:** Phase 23 — complete
- **Post-v2 model gateway:** Phase 24 — complete
- **Post-v2 Termux runtime:** Phase 25 — complete
- **Post-v2 Codespaces runtime:** Phase 26 — complete
- **Post-v2 CLI/setup:** Phase 27 — complete
- **Post-v2 cross-environment handoff:** Phase 28 — complete
- **Post-v2 agent personas:** Phase 29 — reopened

## Phase completion gate

A phase is not complete merely because files exist. Its acceptance criteria must be implemented, relevant tests must pass, CI must verify installation/build/lint/tests, and any CI failure discovered during completion must be fixed and rerun before the phase is declared complete. Documentation must never claim a stronger state than the implementation and verification evidence support.

## Phase 29 current verification record

The original Phase 29 implementation introduced `AgentPersona`, a deterministic Markdown parser, semantic validator, governed compiler, and duplicate-safe persona registry. Seven canonical personas are present and remain regression coverage for that machinery.

The original seven-persona completion claim is superseded by the reopened parity requirement. The pinned Agency Agents snapshot is commit `6d29a9b08785a0e49ffc9818bbdd381164c2df5f`, whose upstream commit message reports **279 agents** and verification of converted outputs across 14 tools. The upstream `divisions.json` defines 18 divisions.

The reopened Phase 29 audit is documented in `PHASE_29_AGENCY_AGENTS_AUDIT.md`. Non-agent Markdown such as documentation, integrations, examples, strategy/playbooks, and runbooks is explicitly excluded from the persona count.

The last pre-reopen mainline documentation CI verification remains valid as regression evidence for the existing implementation: commit `578547786b7cfab96973c5423bef93b970bde6f1`, with the recorded CI suite at 352 passed. It does **not** constitute completion evidence for the reopened 279-persona corpus.

## Phase 28 verification record

Phase 28 is complete on mainline commit `4ccfcfe29693d2a0f76810c000607822938253f4`. GitHub Actions CI run **#526** completed successfully and verified distribution build, isolated wheel installation, installed `si` catalog smoke tests, Ruff, and the full pytest suite with **341 tests passing**. The same verification covered handoff serialization/atomic storage, SHA-256 tamper detection, recursive secret-like field rejection, Termux/Codespaces target validation, repository identity sanitization/canonicalization, resumable context metadata, and Phase 28 CLI parser coverage.

## Documentation structure

The historical architecture record is explicitly indexed from Phase 1 onward:

- `PHASE_1_FOUNDATION.md` — renamed Phase 1 foundation record.
- `PHASE_2_CONTROL_PLANE.md` — consolidated Phase 2 control-plane and execution-boundary record; the duplicate `CONTROL_PLANE.md` has been removed.
- `PHASE_3_*` through `PHASE_29_*` — detailed historical/current phase records.
- `PHASE_29_AGENCY_AGENTS_AUDIT.md` — current reopened Phase 29 audit and parity contract.
- `EXECUTION_BACKENDS.md` — cross-cutting execution-backend boundary.

Historical phase documents preserve phase-time evidence. Current cross-phase state belongs here, and future planning belongs in `SI_AGENTS_V3.md`.

## Next phase

**Phase 30 — First-Class Portable Skills** remains the planned next implementation phase, but it is **blocked** until the reopened Phase 29 parity and verification gate passes.
