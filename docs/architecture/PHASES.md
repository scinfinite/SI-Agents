# SI-Agents Implementation Phases

**Current status: v2.0 baseline plus Phases 19–24 implemented; Phase 24 awaits CI verification.**

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
24. OmniRoute Integration — OpenAI-compatible gateway transport, deterministic model discovery, secure credential handling, fail-closed health/failure classification, correlation/session forwarding, and a governed delegation boundary that keeps provider/model routing authoritative in OmniRoute. **Implementation complete; CI verification pending.**

## Release targets

- **Alpha:** phases 0–5 — achieved
- **Beta:** phases 6–9 — **complete**
- **v1.0:** phases 10–13 — **complete**
- **v1.5:** phases 14–15 — **complete**
- **v2.0:** phases 16–18 — **complete**
- **Post-v2 validation:** Phase 19 — **complete**
- **Post-v2 organization:** Phase 20 — **complete**
- **Post-v2 orchestration:** Phase 21 — **complete**
- **Post-v2 interoperability:** Phase 22 — **complete**
- **Post-v2 OpenCode:** Phase 23 — **complete**
- **Post-v2 model gateway:** Phase 24 — **implementation complete; verification pending**

## Verification rule

A phase is not considered complete merely because its files exist. Its acceptance criteria must be implemented, relevant tests must pass, CI must verify installation/build/lint/tests, and any CI failure discovered during completion must be fixed and rerun before the phase is declared complete.

## Phase 24 completion candidate

Phase 24 adds an external OmniRoute model/provider gateway without creating a second provider-routing authority. `core/provider_intelligence/omniroute.py` provides a stdlib-only OpenAI-compatible client for `/v1/models` and non-streaming `/v1/chat/completions`, deterministic catalog normalization, fail-closed health checks, retryable transport classification, and forwarding of OmniRoute session/idempotency/request-correlation headers. `OmniRouteConfig` defaults to loopback `127.0.0.1:20128`, keeps credentials in memory or an environment variable, and requires HTTPS for non-loopback remote endpoints by default.

`core/provider_intelligence/omniroute_router.py` adds a thin invocation boundary that delegates model/provider routing to OmniRoute. It rejects SI-side cost/latency constraints that cannot be independently verified and rejects `auto` when an SI model allowlist would be required. This avoids shadow pricing, routing, fallback, or circuit-breaker logic around OmniRoute.

Phase 24 intentionally stops before Termux/Codespace installation, the `si` CLI, persistent credential/config management, OpenCode configuration mutation, streaming normalization, cross-environment handoff, and automatic paid-provider activation. Those remain later phases or deployment responsibilities.

The detailed contract is documented in `docs/architecture/PHASE_24_OMNIROUTE_INTEGRATION.md`.

## Phase 23 completion

Phase 23 adds the first vendor-specific harness adapter on top of the Phase 22 universal boundary. `adapters/opencode` uses the OpenCode headless server HTTP API without adding an OpenCode SDK or provider/router dependency. The adapter creates sessions when needed, reuses caller-supplied sessions, sends normalized synchronous messages, emits a normalized completion event containing the OpenCode session identity, and maps universal cancellation to OpenCode's session abort endpoint.

The adapter advertises only capabilities it currently implements: session continuity, tool calls, structured output, and cancellation. Streaming is deliberately fail-closed until OpenCode's SSE event stream can be normalized into the universal event contract. Optional HTTP Basic authentication is accepted in memory only; SI-Agents does not persist OpenCode credentials or provider secrets. Existing runtime registration and Phase 13 governance remain authoritative.

Phase 23 deliberately stops before OmniRoute/model routing, Termux/Codespace installers, the `si` CLI, cross-environment handoff, or additional vendor adapters. The detailed contract is documented in `docs/architecture/PHASE_23_OPENCODE_INTEGRATION.md`.

Verification evidence: PR #11 CI run **#470** passed distribution build, isolated wheel installation/import including `adapters.opencode`, Ruff, and the complete pytest suite with **299 tests passing**. The PR was merged as commit **bf955386a4b6dff39161af77ef01cb76c1db1246**. Mainline CI run **#471** subsequently passed build, wheel verification, Ruff, and the full pytest suite with **299 tests passing**.

## Phase 22 completion

Phase 22 extends the Phase 17 runtime boundary without coupling the core to a vendor harness. `core/runtime/wire.py` defines the versioned `si.runtime.v1` JSON-compatible envelope; `core/runtime/bridge.py` provides a callback-based adapter bridge and normalized metadata discovery; and `core/runtime/deployment.py` provides a deterministic organization exposure manifest for Phase 20/21 agents, teams, skills, permissions, and capabilities.

Deployment manifests are descriptive only. They do not enable harnesses, grant permissions, invoke workers, bypass governance, or install configuration. The existing deny-by-default harness registry, session isolation, capability checks, and governance decision remain authoritative.

Phase 22 deliberately stops before vendor-specific integration. OpenCode, Codex, Claude Code, Cline, Antigravity, OmniRoute, Termux, Codespaces, and installation/configuration workflows remain subsequent phases or deployment responsibilities.

Verification evidence: PR #7 CI run **#465** passed distribution build, isolated wheel installation/import, Ruff, and the complete pytest suite with **293 tests passing**. The PR was merged as commit **4daa68732ddd515b5033ec3a1516be418c0bf4fb**. Mainline CI run **#466** subsequently passed the same build, wheel verification, Ruff, and full test suite on `main`.

## Phase 21 completion

Phase 21 adds the executable organization/team layer on top of Phase 20. `config/team-catalog.json` is the canonical source for declarative team/workflow definitions. `core/teams` provides typed team/task/execution/event contracts, a duplicate-safe registry, a stdlib-only loader, and a bounded dependency-aware executor.

The workflow engine schedules a dependency DAG deterministically, limits concurrency with team-level `max_parallelism`, supports explicit shared or isolated task context, uses `AgentResult.handoff` for portable handoffs, bounds retries, supports explicit escalation to declared team members, blocks downstream work after dependency failure, supports cooperative cancellation, and records ordered workflow events plus a final evidence checkpoint.

Team membership does not grant permissions or governance authority. Workers are injected into the engine and remain responsible for their existing permission checks; the existing governance/runtime layers remain authoritative. This preserves the separation established by Phases 13, 17, and 18.

The canonical `engineering-repair` workflow models debugger → developer → tester sequencing with evidence and verification gates. The acceptance suite covers dependency handoff, shared/isolated context, bounded parallelism, retry, escalation, verification/evidence gates, blocked downstream work, cancellation, cycle rejection, duplicate team rejection, and canonical catalog loading.

Final verification evidence: CI run **#450** passed distribution build, isolated wheel installation/import, Ruff, and the complete pytest suite, with **284 tests passing**. The final completion fixes included enforcing isolated-context non-publication and keeping verification gates active during escalation.

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
