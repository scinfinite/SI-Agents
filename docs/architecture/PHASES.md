# SI-Agents Implementation Phases

**Current status: v2.0 baseline plus Phases 19–28 implemented and CI-verified.**

> This file is the authoritative historical implementation/status record. `docs/architecture/SI_AGENTS_V3.md` is the forward-looking roadmap for Phases 29–43. `docs/README.md` is the documentation navigation index.

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

## Phase completion gate

A phase is not complete merely because files exist. Its acceptance criteria must be implemented, relevant tests must pass, CI must verify installation/build/lint/tests, and any CI failure discovered during completion must be fixed and rerun before the phase is declared complete. Documentation must never claim a stronger state than the implementation and verification evidence support.

## Phase 28 verification record

Phase 28 is complete on mainline commit `4ccfcfe29693d2a0f76810c000607822938253f4`. GitHub Actions CI run **#526** completed successfully and verified distribution build, isolated wheel installation, installed `si` catalog smoke tests, Ruff, and the full pytest suite with **341 tests passing**. The same verification covered handoff serialization/atomic storage, SHA-256 tamper detection, recursive secret-like field rejection, Termux/Codespaces target validation, repository identity sanitization/canonicalization, resumable context metadata, and Phase 28 CLI parser coverage.

CI #525 exposed two real defects—JSON sequence fields did not normalize back to typed tuples, and SSH repository identity canonicalization retained the `git@` transport prefix. Both were fixed and CI #526 passed. No failure was suppressed or reclassified as success.

The detailed contract is `PHASE_28_CROSS_ENVIRONMENT_HANDOFF.md`.

## Phase 27 verification record

Phase 27 added the `si` console entry point and a single user-facing control surface over existing SI-Agents contracts. `si doctor` delegates to environment readiness; `si status` reports non-secret configuration; `si agents` and `si teams` load canonical catalogs; `si setup` is dry-run by default and requires `--apply` for mutation; `si update` requires `--apply`; and `si run` executes canonical teams through `TeamEngine` without creating a second permission system.

Verification evidence: PR #14 CI run **#499** passed distribution build, isolated wheel installation/import plus installed `si agents`/`si teams` catalog checks, Ruff, and the complete pytest suite with **330 tests passing**. Earlier #495 and #497 failures exposed and corrected a Ruff exception-type defect and a parser-coverage defect. The merged implementation was followed by mainline verification.

## Phase 26 verification record

Phase 26 added the read-only Codespaces readiness boundary. It detects Codespaces, validates Python/Git/curl/OpenSSH/workspace requirements, optionally requires GitHub CLI and OmniRoute, validates OpenCode readiness, and exposes a non-executing toolchain plan plus sanitized doctor output. Verification evidence: mainline CI #494 passed distribution build, isolated wheel installation/import, Ruff, and the full pytest suite with **327 tests passing** after fixing #493.

## Phase 25 verification record

Phase 25 added Termux readiness contracts, detection, command checks, OpenCode readiness, optional fail-closed OmniRoute health, read-only doctor, secret-free JSON reporting, conservative package planning, and workspace validation. Verification evidence: PR #13 CI #485 passed build, isolated wheel verification, Ruff, and **319 tests passing**; #482 exposed a Ruff SIM114 issue that was fixed before the successful run.

## Phase 24 verification record

Phase 24 added the stdlib-only OmniRoute gateway client and governed invocation boundary while keeping provider/model routing authoritative in OmniRoute. Verification evidence: PR #12 CI #478 passed build, isolated wheel verification, Ruff, and **310 tests passing**; mainline #479 passed afterward.

## Phase 23 verification record

Phase 23 added the vendor-specific OpenCode headless-server adapter on top of the universal runtime boundary. Streaming remains fail-closed until it can be normalized safely. Verification evidence: PR #11 CI #470 and mainline #471 passed build, isolated wheel verification, Ruff, and **299 tests passing**.

## Phase 22 verification record

Phase 22 added the versioned `si.runtime.v1` wire envelope, callback bridge, normalized metadata, and descriptive organization deployment manifests. Verification evidence: PR #7 CI #465 and mainline #466 passed with **293 tests** and distribution/wheel/Ruff gates.

## Phase 21 verification record

Phase 21 added canonical teams/workflows, deterministic dependency-DAG scheduling, bounded parallelism, context isolation, handoffs, retries, escalation, evidence gates, cancellation, checkpoints, and workflow events. Final CI #450 passed with **284 tests**.

## Phase 20 verification record

Phase 20 established the canonical organization layer with 7 divisions and 12 agent definitions, typed contracts, duplicate-safe registration, deterministic selection, and validation. Final main CI #442 passed all required gates.

## Phase 19 verification record

Phase 19 established the evidence-backed post-v2 boundary through executable audit, runtime E2E, distribution correctness, isolated wheel verification, and explicit future-boundary definition. PR #2 CI #431 passed all required gates; baseline #428 and documentation synchronization #429 were also successful.

## Detailed phase documents

Historical phase contracts are retained as `PHASE_<n>_*.md` documents in this directory. They describe the scope and evidence for the phase at completion time and should not be rewritten to imply later capabilities. Current status belongs here; future planning belongs in `SI_AGENTS_V3.md`.

## Next phase

**Phase 29 — Agent Persona & Definition System** is the next implementation phase. It must begin only from the verified Phase 28 baseline and the synchronized documentation set.
