# SI-Agents

SI-Agents is an evidence-driven AI engineering system designed to inspect software, diagnose problems, execute controlled changes, verify results, and learn reusable engineering patterns.

## Current status

**Post-v2 evolution — Phases 19–26 implemented and CI-verified; Phase 27 implementation complete and CI verification in progress.**

Completed foundation through Production Hardening and the post-v2 organization, orchestration, interoperability, OpenCode, OmniRoute, Termux, GitHub Codespaces, and user-facing CLI/setup layers:

- **Phase 1 — Foundation:** architecture, engineering rules, governance, project isolation, security/cost/learning/compliance policies, provenance controls, and verification standards.
- **Phase 2 — Control Plane:** task lifecycle, persistence, dependencies, retries, context isolation, agents, workflows, permissions, approvals, checkpoints, execution state, and evidence integration.
- **Phase 3 — Tool System:** controlled filesystem, terminal, Git, GitHub, web, code analysis, build/test, container, sandbox, and artifact tooling with registry and permission enforcement.
- **Phase 4 — Engineering Brain:** problem normalization, decomposition, dependency-aware planning, reasoning, hypotheses, root-cause analysis, trade-offs, uncertainty, risk, and capability-aware planning.
- **Phase 5 — Developer/Debugger/Tester:** explicit agent contracts and the inspect → reproduce → diagnose → checkpoint → repair → test → red-team → regression → verify → document workflow.
- **Phase 6 — Skills Engine:** reusable skill contracts, lifecycle states, validated selection, permissioned execution, explicit verification, evidence recording, and an initial engineering skill catalog.
- **Phase 7 — Verification + Evidence:** bounded claims, provenance-aware evidence, confidence assessment, fail-closed verification, regression suites, red-team falsification, before/after benchmarks, and production-readiness gates.
- **Phase 8 — Technical Knowledge:** universal language schema, provenance-aware knowledge contracts, runtime catalog loading, multi-language coverage, framework/ecosystem catalog, and engineering standards catalog.
- **Phase 9 — Technology Discovery:** repository technology/build detection, explicit uncertainty, safe experimentation contracts, declaration-based compatibility checks, and provenance-preserving knowledge proposals.
- **Phase 10 — Open-Source Intelligence:** repository metadata, archaeology/history, issues, pull requests, releases, security advisories, conservative license assessment, project health, freshness, and a read-only provider contract.
- **Phase 11 — Pattern Extraction:** deterministic observation normalization, conservative candidate extraction, independent evidence validation, counterexample handling, evidence-gated promotion, versioning, provenance, and context matching.
- **Phase 12 — Engineering Memory:** task/project/global scopes, provenance and verified evidence, fail-closed one-step promotion, deterministic scoped retrieval, expiration, supersession/versioning, and auditable JSON persistence.
- **Phase 13 — Security + Legal + Cost:** executable governance decisions, conservative risk classification, data-egress controls, provenance/legal review, free-first paid-resource controls, explicit approvals, and audit evidence.
- **Phase 14 — Model/Provider Intelligence:** typed model/provider capabilities, explicit registration, quota observations, deterministic capability/cost/latency routing, reliability/health tracking, fallback constraints, and provider circuit breakers.
- **Phase 15 — Automation:** one-shot/recurring schedules, deterministic due selection, lifecycle controls, registered actions, conditional triggers, bounded retries/backoff, idempotency, governance-gated execution, run history, and dependency-free JSON persistence.
- **Phase 16 — Controlled Self-Improvement + Capability Intelligence:** evidence-backed improvement proposals, benchmark/regression/safety gates, explicit approval, rollback, deterministic capability readiness scoring, conservative unknown handling, and auditable JSON persistence.
- **Phase 17 — Harness & Runtime Interoperability:** transport-neutral invocation envelopes, runtime capability negotiation, normalized events/errors, project-scoped sessions, explicit harness registry, governed local adapter, and adapter conformance testing.
- **Phase 18 — Production Hardening:** deterministic readiness checks, explicit resource limits, conservative telemetry redaction, evidence-based release gates, production policy, migration/rollback requirements, and hardened CI execution.
- **Phase 19 — v2.0 Reality Audit:** executable baseline audit, distribution correctness, isolated wheel verification, runtime E2E acceptance, and explicit future-boundary definition. **Complete and CI-verified.**
- **Phase 20 — Agent Organization & Catalog:** canonical divisions and agent definitions, typed catalog registry, declarative capability/permission/environment/harness selection, lifecycle status, implementation references, and validation tests. **Complete and CI-verified.**
- **Phase 21 — Agent Teams & Workflows:** canonical team/workflow catalog, dependency-aware DAG execution, bounded parallelism, shared/isolated context, explicit handoffs, retries, escalation, evidence/verification gates, cancellation, checkpoints, and auditable workflow events. **Complete and CI-verified.**
- **Phase 22 — Universal Harness Integration:** versioned `si.runtime.v1` wire contract, callback-based universal adapter bridge, normalized harness metadata, and deterministic organization deployment manifests. **Complete and CI-verified.**
- **Phase 23 — OpenCode Integration:** stdlib-only OpenCode headless-server adapter, session creation/continuity, normalized synchronous messages, request-to-session cancellation, optional in-memory HTTP basic authentication, and fail-closed streaming capability declaration. **Complete and CI-verified.**
- **Phase 24 — OmniRoute Integration:** stdlib-only OpenAI-compatible gateway client, deterministic model discovery, fail-closed health checks, secure credential handling, retryable transport classification, session/idempotency/request correlation forwarding, and a governed invocation layer that delegates provider/model routing to OmniRoute. **Complete and CI-verified.**
- **Phase 25 — Termux Runtime:** vendor-neutral environment readiness contracts, Termux detection, Python/Git/curl/OpenSSH/pkg checks, OpenCode readiness, optional fail-closed OmniRoute health, read-only Termux doctor, secret-free JSON reporting, conservative package planning, and workspace validation. **Complete and CI-verified.**
- **Phase 26 — GitHub Codespaces Runtime:** Codespaces detection, Python/Git/curl/OpenSSH/workspace checks, OpenCode readiness, optional GitHub CLI and OmniRoute requirements, read-only toolchain planning, workspace validation, and secret-free doctor reporting. **Complete and CI-verified.**
- **Phase 27 — `si` CLI + Easy Setup:** user-facing doctor/status/agents/teams/setup/update/run commands, non-secret configuration, explicit mutation gates, safe OpenCode OmniRoute configuration, and governed team execution. **Implementation complete; CI verification in progress.**

## `si` CLI

```text
si doctor [--json]
si status
si agents
si teams
si setup [--apply] [--configure-opencode] [--model MODEL]
si update [--apply]
si run TEAM --objective TEXT
```

`doctor`, `status`, `agents`, and `teams` are read-only. `setup` and `update` are dry-run by default and require `--apply` before mutation. Setup commands come from the existing environment runtime plan and are checked against an allowlist; arbitrary shell strings are rejected.

The CLI stores only non-secret configuration at `~/.config/si-agents/config.json` by default (or `SI_CONFIG`), using atomic replacement and restrictive permissions. No API key, password, provider credential, or OpenCode auth token is stored by SI-Agents.

With `si setup --configure-opencode --model <model> --apply`, the CLI can add/update an OmniRoute OpenAI-compatible provider in the current OpenCode JSON configuration. It refuses JSONC rather than rewriting it unsafely and requires an explicit model instead of guessing capabilities from OmniRoute's mixed `/v1/models` catalog.

`si run` executes canonical Phase 21 teams through the existing TeamEngine and worker/runtime governance. The CLI does not grant permissions, enable disabled harnesses, bypass approvals, or replace OmniRoute routing.

See `docs/architecture/PHASE_27_SI_CLI.md` for the detailed Phase 27 contract and `docs/architecture/PHASES.md` for the roadmap.

## Engineering loop

```text
OBSERVE → UNDERSTAND → RESEARCH → PLAN → EXECUTE → MEASURE
→ TEST → ATTACK THE SOLUTION → VERIFY → DOCUMENT → LEARN → GENERALIZE → REUSE
```

## Control and safety model

Agents, capabilities, tools, skills, knowledge, automation jobs, teams, harness adapters, and environment runtimes are workers/data—not policy authorities. Registration or selection does not grant permission. High-risk actions remain approval-gated, repository mutation remains protected, and important claims require evidence.

OpenCode integration is a transport boundary, not a model/provider router. OpenCode owns its server, provider credentials, and harness lifecycle. SI-Agents sends normalized runtime requests and consumes normalized results. OmniRoute is the external model/provider routing authority for Phase 24 and remains so inside the Termux and Codespaces runtimes and Phase 27 CLI setup.

Phase 24 deliberately does not create a second provider-fallback or circuit-breaker system around OmniRoute. OmniRoute owns provider selection, upstream credentials, provider fallback, gateway-side quotas, routing policies, and provider circuit state. SI-Agents owns its invocation contract and fail-closed local governance boundaries.

Phase 25 and Phase 26 provide read-only environment readiness. Phase 27 is the first explicit mutation layer: setup/update actions require `--apply`, execution is allowlisted, credentials are not persisted, and OpenCode configuration is changed only through a narrow, parse-safe provider configuration path.

Universal harness deployment is descriptive, not authoritative. A deployment manifest can describe agents, teams, skills, required permissions, and capabilities for a harness, but it cannot enable the harness, grant permissions, execute workers, or bypass governance. Vendor-specific adapters remain separate from the core.
