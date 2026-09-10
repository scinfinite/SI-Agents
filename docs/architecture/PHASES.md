# SI-Agents Implementation Phases

**Current status: v2.0 baseline plus Phases 19–27 implemented in code; Phase 27 CI verification is in progress on PR #14.**

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
27. `si` CLI + Easy Setup — user-facing doctor/status/catalog/team/setup/update/run commands, non-secret configuration, explicit mutation gates, OpenCode OmniRoute configuration, and governed team execution. **Implementation complete; CI verification pending.**

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
- **Post-v2 model gateway:** Phase 24 — **complete**
- **Post-v2 Termux runtime:** Phase 25 — **complete**
- **Post-v2 Codespaces runtime:** Phase 26 — **complete**
- **Post-v2 CLI/setup:** Phase 27 — **implementation complete; CI verification pending**

## Verification rule

A phase is not considered complete merely because its files exist. Its acceptance criteria must be implemented, relevant tests must pass, CI must verify installation/build/lint/tests, and any CI failure discovered during completion must be fixed and rerun before the phase is declared complete.

## Phase 27 completion

Phase 27 adds the `si` console entry point and a single user-facing control surface over the existing SI-Agents contracts. `si doctor` delegates to the Termux/Codespaces readiness contracts; `si status` reports environment and non-secret configuration; `si agents` and `si teams` load the canonical Phase 20/21 catalogs; `si setup` provides a dry-run by default and requires `--apply` for local mutation; `si update` requires `--apply` before package upgrade; and `si run` executes canonical teams through `TeamEngine` without creating a second permission system.

The CLI stores only non-secret configuration at `~/.config/si-agents/config.json` by default, with atomic replacement and restrictive permissions. No API key, OpenCode password, provider credential, or auth token is stored. OpenCode configuration is updated only when explicitly requested and only for a JSON configuration that can be parsed safely; JSONC is refused rather than destructively rewritten. OmniRoute remains the model/provider routing authority and an explicit model ID is required before adding a model to the OpenCode OmniRoute provider configuration.

Setup execution is limited to commands supplied by the existing environment runtime plan and checked against an allowlist. The CLI never accepts arbitrary shell strings. Read-only operations do not mutate the host. Team execution uses existing worker, runtime, and governance boundaries; catalog-only agents are not made executable by the CLI.

Detailed architecture: `docs/architecture/PHASE_27_SI_CLI.md`.

Verification evidence is pending until PR #14 CI completes. The acceptance target is distribution build, isolated wheel installation/import, Ruff, and the complete pytest suite, followed by documentation synchronization after any discovered defects are fixed.

## Phase 26 completion

Phase 26 adds the equivalent read-only readiness boundary for GitHub Codespaces. `core/environments/codespace.py` detects Codespaces, validates Python/Git/curl/OpenSSH/workspace requirements, optionally requires GitHub CLI and OmniRoute, validates OpenCode readiness, and exposes a non-executing toolchain plan plus sanitized doctor output. Exit codes remain `0` ready, `2` degraded, and `3` unsupported.

The Codespaces runtime never creates/configures a Codespace, installs packages, mutates OpenCode configuration, persists credentials, or executes arbitrary commands. Cross-environment synchronization and the user-facing `si` setup layer remain separate responsibilities.

Verification evidence: mainline CI run **#494** passed distribution build, isolated wheel installation/import, Ruff, and the full pytest suite with **327 tests passing** after an initial #493 Ruff F841 defect was fixed.

## Phase 25 completion

Phase 25 makes SI-Agents inspectable and operationally ready inside Termux without turning readiness checks into an implicit installer or command-execution authority. `core/environments/models.py` defines vendor-neutral environment kinds, statuses, and sanitized requirement/report contracts. `core/environments/termux.py` implements Termux detection, required command checks for Python/Git/curl/OpenSSH/pkg, OpenCode readiness, optional fail-closed OmniRoute health, read-only workspace validation, a conservative package plan, and a direct doctor command available as `python -m core.environments.termux`.

The doctor supports human-readable and `--json` output. Exit code `0` means ready, `2` means degraded, and `3` means unsupported. JSON reports expose only readiness metadata and never emit API-key values. The runtime never installs packages, mutates OpenCode configuration, persists OmniRoute credentials, executes arbitrary commands, or bypasses Phase 13 governance and Phase 24 OmniRoute authority.

The Termux runtime intentionally validates the presence of OpenCode rather than pinning a harness release. The package plan is descriptive only and currently covers `pkg update` plus `git`, `python`, `curl`, and `openssh`. Explicit installation/configuration is provided by the Phase 27 `si` setup layer. The detailed contract is documented in `docs/architecture/PHASE_25_TERMUX_RUNTIME.md`.

Verification evidence: PR #13 CI run **#485** passed distribution build, isolated wheel installation/import, Ruff, and the complete pytest suite with **319 tests passing**. An initial CI attempt (#482) found a Ruff SIM114 issue; it was fixed and the corrected run passed. The PR was merged as commit **cf1962870c979ebbf21fac5b6f3bc304f7af76ee**. Mainline CI run **#486** passed after merge.

## Phase 24 completion

Phase 24 adds an external OmniRoute model/provider gateway without creating a second provider-routing authority. `core/provider_intelligence/omniroute.py` provides a stdlib-only OpenAI-compatible client for `/v1/models` and non-streaming `/v1/chat/completions`, deterministic catalog normalization, fail-closed health checks, retryable transport classification, and forwarding of OmniRoute session/idempotency/request-correlation headers. `OmniRouteConfig` defaults to loopback `127.0.0.1:20128`, keeps credentials in memory or an environment variable, and requires HTTPS for non-loopback remote endpoints by default.

`core/provider_intelligence/omniroute_router.py` adds a thin invocation boundary that delegates model/provider routing to OmniRoute. It rejects SI-side cost/latency constraints that cannot be independently verified and rejects `auto` when an SI model allowlist would be required. This avoids shadow pricing, routing, fallback, or circuit-breaker logic around OmniRoute.

Phase 24 intentionally stops before Termux/Codespace installation, the `si` CLI, persistent credential/config management, OpenCode configuration mutation, streaming normalization, cross-environment handoff, and automatic paid-provider activation. Those were subsequent phases.

The detailed contract is documented in `docs/architecture/PHASE_24_OMNIROUTE_INTEGRATION.md`.

Verification evidence: PR #12 CI run **#478** passed distribution build, isolated wheel installation/import, Ruff, and the complete pytest suite with **310 tests passing**. The PR was merged as commit **8d3867c931db232c7c2bcc620d448f8cb30de735**. Mainline CI run **#479** subsequently passed build, wheel verification, Ruff, and the full pytest suite on `main`.

## Phase 23 completion

Phase 23 adds the first vendor-specific harness adapter on top of the Phase 22 universal boundary. `adapters/opencode` uses the OpenCode headless server HTTP API without adding an OpenCode SDK or provider/router dependency. The adapter creates sessions when needed, reuses caller-supplied sessions, sends normalized synchronous messages, emits a normalized completion event containing the OpenCode session identity, and maps universal cancellation to OpenCode's session abort endpoint.

The adapter advertises only capabilities it currently implements: session continuity, tool calls, structured output, and cancellation. Streaming is deliberately fail-closed until OpenCode's SSE event stream can be normalized into the universal event contract. Optional HTTP Basic authentication is accepted in memory only; SI-Agents does not persist OpenCode credentials or provider secrets. Existing runtime registration and Phase 13 governance remain authoritative.

Verification evidence: PR #11 CI run **#470** passed distribution build, isolated wheel installation/import including `adapters.opencode`, Ruff, and the complete pytest suite with **299 tests passing**. The PR was merged as commit **bf955386a4b6dff39161af77ef01cb76c1db1246**. Mainline CI run **#471** subsequently passed build, wheel verification, Ruff, and the full pytest suite with **299 tests passing**.

## Phase 22 completion

Phase 22 extends the Phase 17 runtime boundary without coupling the core to a vendor harness. `core/runtime/wire.py` defines the versioned `si.runtime.v1` JSON-compatible envelope; `core/runtime/bridge.py` provides a callback-based adapter bridge and normalized metadata discovery; and `core/runtime/deployment.py` provides a deterministic organization exposure manifest for Phase 20/21 agents, teams, skills, permissions, and capabilities.

Deployment manifests are descriptive only. They do not enable harnesses, grant permissions, invoke workers, bypass governance, or install configuration. The existing deny-by-default harness registry, session isolation, capability checks, and governance decision remain authoritative.

Verification evidence: PR #7 CI run **#465** passed distribution build, isolated wheel installation/import, Ruff, and the complete pytest suite with **293 tests passing**. The PR was merged as commit **4daa68732ddd515b5033ec3a1516be418c0bf4fb**. Mainline CI run **#466** subsequently passed the same build, wheel verification, Ruff, and full test suite on `main`.

## Phase 21 completion

Phase 21 adds the executable organization/team layer on top of Phase 20. `config/team-catalog.json` is the canonical source for declarative team/workflow definitions. `core/teams` provides typed team/task/execution/event contracts, a duplicate-safe registry, a stdlib-only loader, and a bounded dependency-aware executor.

The workflow engine schedules a dependency DAG deterministically, limits concurrency with team-level `max_parallelism`, supports explicit shared or isolated task context, uses `AgentResult.handoff` for portable handoffs, bounds retries, supports explicit escalation to declared team members, blocks downstream work after dependency failure, supports cooperative cancellation, and records ordered workflow events plus a final evidence checkpoint.

The canonical `engineering-repair` workflow models debugger → developer → tester sequencing with evidence and verification gates. Final CI run **#450** passed with **284 tests passing** after isolated-context publication and escalation-gate fixes.

## Phase 20 completion

Phase 20 establishes the first canonical organization layer. `config/agent-catalog.json` is the source of truth for 7 divisions and 12 agent definitions. `core/organization` provides typed definitions, lifecycle status, duplicate-safe registration, deterministic lookup/grouping, and selection by skills, capabilities, permissions, harness, environment, and status. Implemented roles reference existing Python workers; catalog-only roles remain declarative.

Verification evidence: final main CI run **#442** passed distribution build, isolated wheel installation/import, Ruff, and the full pytest suite.

## Phase 19 completion

Phase 19 established the evidence-backed boundary for the next SI-Agents evolution. The audit confirmed that the v2.0 runtime boundary is executable and governed, while identifying the missing user-facing cross-harness/environment layer. The `agents` package distribution gap was fixed; CI installs the built wheel in an isolated environment and a dedicated integration test exercises a registered, enabled, governed runtime session.

Verification evidence: PR #2 CI run **#431** completed successfully with distribution build, isolated wheel installation/import, Ruff, and the full pytest suite. Main baseline CI run #428 and status synchronization PR #1 CI run #429 were also successful.

## Phase 18 completion

Phase 18 hardens the platform for production operation without overstating guarantees. Readiness checks are deterministic and fail closed on check failures; application-level resource limits bound accepted work; telemetry representations redact secret-like fields and bearer credentials; and a release gate requires evidence for tests, lint, build, security review, migration review, and rollback testing.

Production hardening does not replace Phase 13 governance or turn the local executor into a security boundary. Infrastructure controls and operator procedures remain deployment responsibilities.

## Phase 17 completion

Phase 17 establishes a vendor-neutral runtime boundary. CLI, API, IDE, agent, embedded, and future harnesses use a typed invocation envelope with stable correlation, project identity, optional sessions, declared capabilities, normalized events, and structured errors. Harnesses are explicitly registered and disabled by default, and the reference local adapter requires the existing Phase 13 governance decision before execution.

## Phase 16 completion

Phase 16 delivers a controlled learning pipeline in which evidence-backed proposals are evaluated through independent benchmark, regression, and safety gates before explicit approval. Application and rollback are externally supplied operations, so the learning engine cannot silently mutate code. Automatic code mutation, automatic capability promotion, automatic global promotion, and secret storage remain disabled by policy.

## Prior phase completion

Phases 10–15 delivered provenance-preserving open-source intelligence, evidence-gated pattern extraction, scoped engineering memory, executable security/legal/cost governance, typed model/provider intelligence, and governance-gated automation. Their existing completion documents remain authoritative for their respective acceptance criteria and verification evidence.
