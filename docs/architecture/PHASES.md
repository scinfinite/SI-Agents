# SI-Agents Implementation Phases

**Current status: v2.0 baseline plus Phases 19–30 complete; Phase 31 implementation complete pending final mainline CI.**

> This file is the authoritative current implementation/status record. `docs/architecture/SI_AGENTS_V3.md` is the forward-looking roadmap. `docs/README.md` and `docs/architecture/README.md` are documentation navigation indexes.

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
29. Complete SI Agent Persona System — **Complete and CI-verified.** Exactly 279 SI-native specialist personas are organized across 18 SI-owned domain divisions, with deterministic parsing, typed catalog parity, security checks, repository-neutral provenance, packaging coverage, and CI verification.
30. First-Class Portable Skills — **Complete and CI-verified.** Portable `SKILL.md` artifacts, deterministic parsing/validation/registry, dependency-aware composition, artifact manifests, governed execution, explicit verification/evidence, six canonical Skills, CLI integration, packaging, regression coverage, and safety boundaries are implemented.
31. Rules, Hooks & Event System — **Implementation complete; final mainline CI pending.** Explicit immutable events, deterministic Rules, bounded in-process Hooks, fail-closed dangerous-event handling, Skill event integration, declarative Rule catalog, packaging, regression/adversarial tests, and current documentation are implemented.

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
- **Post-v2 SI persona system:** Phase 29 — complete
- **Post-v2 portable Skills:** Phase 30 — complete
- **Post-v2 Rules/Hooks/Events:** Phase 31 — implementation complete, final CI pending

## Phase completion gate

A phase is not complete merely because files exist. Its acceptance criteria must be implemented, relevant tests must pass, CI must verify installation/build/lint/tests, and any CI failure discovered during completion must be fixed and rerun before the phase is declared complete. Documentation must never claim a stronger state than the implementation and verification evidence support.

## Phase 30 verification record

Phase 30 was merged to `main` as commit `62972acf20a0da53bf81161c2108a506dbdad907` from PR #17 after its CI passed. Mainline CI run **#727** completed successfully on that merge commit. The Phase 30 Skill catalog contains six canonical Skills with deterministic parsing/validation, dependency composition, SHA-256 artifact manifests, explicit permission and verification gates, CLI discovery/inspection/composition, packaging, and regression coverage.

## Phase 31 verification record

Phase 31 uses `core/events`, `core/rules`, and `core/hooks`. Event payloads are immutable, bounded, and secret-key redacted. Rules are exact-match declarative data and never execute expressions or commands. Hooks are explicitly registered in-process handlers with deterministic ordering, per-event limits, runtime budgets, observer/gate separation, and fail-closed gate errors. Dangerous events fail closed when no applicable Rule exists. `SkillExecutor` can publish Skill and verification lifecycle events through the EventBus without replacing the existing PermissionEngine/GovernanceEngine authority.

The canonical Rule catalog is `config/rules.v1.json`; the canonical Phase 31 architecture and acceptance record is `PHASE_31.md`.

## Documentation structure

- `PHASE_1_FOUNDATION.md` — renamed Phase 1 foundation record.
- `PHASE_2_CONTROL_PLANE.md` — consolidated Phase 2 control-plane and execution-boundary record; duplicate `CONTROL_PLANE.md` removed.
- `PHASE_3_*` through `PHASE_28_*` — detailed historical phase records.
- `PHASE_29.md` — canonical SI persona, parity, provenance, security, packaging, and verification record.
- `PHASE_30.md` — canonical portable Skill contract and verification record.
- `PHASE_31.md` — canonical Rules/Hooks/Events contract and verification record.
- `EXECUTION_BACKENDS.md` — cross-cutting execution-backend boundary.

Historical phase documents preserve phase-time evidence. Current cross-phase state belongs here, and future planning belongs in `SI_AGENTS_V3.md`.

## Next phase

**Phase 32 — Memory & Knowledge** is next after Phase 31 final mainline CI verification.
