# SI-Agents

SI-Agents is an evidence-driven AI engineering system designed to inspect software, diagnose problems, execute controlled changes, verify results, and learn reusable engineering patterns.

## Current status

**Post-v2 evolution — Phases 19–29 implemented and CI-verified.**

Completed foundation through Production Hardening and the post-v2 organization, orchestration, interoperability, OpenCode, OmniRoute, Termux, GitHub Codespaces, CLI/setup, cross-environment handoff, and human-authored agent persona layers.

- **Phase 1 — Foundation:** architecture, engineering rules, governance, project isolation, security/cost/learning/compliance policies, provenance controls, and verification standards. **Complete.**
- **Phase 2 — Control Plane:** task lifecycle, persistence, dependencies, retries, context isolation, agents, workflows, permissions, approvals, checkpoints, execution state, and evidence integration. **Complete.**
- **Phase 3 — Tool System:** controlled filesystem, terminal, Git, GitHub, web, code analysis, build/test, container, sandbox, and artifact tooling with registry and permission enforcement. **Complete.**
- **Phase 4 — Engineering Brain:** problem normalization, decomposition, dependency-aware planning, reasoning, hypotheses, root-cause analysis, trade-offs, uncertainty, risk, and capability-aware planning. **Complete.**
- **Phase 5 — Developer/Debugger/Tester:** explicit agent contracts and the inspect → reproduce → diagnose → checkpoint → repair → test → red-team → regression → verify → document workflow. **Complete.**
- **Phase 6 — Skills Engine:** reusable skill contracts, lifecycle states, validated selection, permissioned execution, explicit verification, evidence recording, and an initial engineering skill catalog. **Complete.**
- **Phase 7 — Verification + Evidence:** bounded claims, provenance-aware evidence, confidence assessment, fail-closed verification, regression suites, red-team falsification, before/after benchmarks, and production-readiness gates. **Complete.**
- **Phase 8 — Technical Knowledge:** universal language schema, provenance-aware knowledge contracts, runtime catalog loading, multi-language coverage, framework/ecosystem catalog, and engineering standards catalog. **Complete.**
- **Phase 9 — Technology Discovery:** repository technology/build detection, explicit uncertainty, safe experimentation contracts, declaration-based compatibility checks, and provenance-preserving knowledge proposals. **Complete.**
- **Phase 10 — Open-Source Intelligence:** repository metadata, archaeology/history, issues, pull requests, releases, security advisories, conservative license assessment, project health, freshness, and a read-only provider contract. **Complete.**
- **Phase 11 — Pattern Extraction:** deterministic observation normalization, conservative candidate extraction, independent evidence validation, counterexample handling, evidence-gated promotion, versioning, provenance, and context matching. **Complete.**
- **Phase 12 — Engineering Memory:** task/project/global memory, provenance and verified evidence, fail-closed one-step promotion, deterministic scoped retrieval, expiration, supersession/versioning, and auditable JSON persistence. **Complete.**
- **Phase 13 — Security + Legal + Cost:** executable governance decisions, conservative risk classification, data-egress controls, provenance/legal review, free-first paid-resource controls, explicit approvals, and audit evidence. **Complete.**
- **Phase 14 — Model/Provider Intelligence:** typed model/provider capabilities, explicit registration, quota observations, deterministic capability/cost/latency routing, reliability/health tracking, fallback constraints, and provider circuit breakers. **Complete.**
- **Phase 15 — Automation:** one-shot/recurring schedules, deterministic due selection, lifecycle controls, registered actions, conditional triggers, bounded retries/backoff, idempotency, governance-gated execution, run history, and dependency-free JSON persistence. **Complete.**
- **Phase 16 — Controlled Self-Improvement + Capability Intelligence:** evidence-backed improvement proposals, benchmark/regression/safety gates, explicit approval, rollback, deterministic capability readiness scoring, conservative unknown handling, and auditable JSON persistence. **Complete.**
- **Phase 17 — Harness & Runtime Interoperability:** transport-neutral invocation envelopes, runtime capability negotiation, normalized events/errors, project-scoped sessions, explicit harness registry, governed local adapter, and adapter conformance testing. **Complete.**
- **Phase 18 — Production Hardening:** deterministic readiness checks, explicit resource limits, conservative telemetry redaction, evidence-based release gates, production policy, migration/rollback requirements, and hardened CI execution. **Complete.**
- **Phase 19 — v2.0 Reality Audit:** executable baseline audit, distribution correctness, isolated wheel verification, runtime E2E acceptance, and explicit future-boundary definition. **Complete and CI-verified.**
- **Phase 20 — Agent Organization & Catalog:** canonical divisions and agent definitions, typed catalog registry, declarative capability/permission/environment/harness selection, lifecycle status, implementation references, and validation tests. **Complete and CI-verified.**
- **Phase 21 — Agent Teams & Workflows:** canonical team/workflow catalog, dependency-aware DAG execution, bounded parallelism, shared/isolated context, explicit handoffs, retries, escalation, evidence/verification gates, cancellation, checkpoints, and auditable workflow events. **Complete and CI-verified.**
- **Phase 22 — Universal Harness Integration:** versioned `si.runtime.v1` wire contract, callback-based universal adapter bridge, normalized harness metadata, and deterministic organization deployment manifests. **Complete and CI-verified.**
- **Phase 23 — OpenCode Integration:** stdlib-only OpenCode headless-server adapter, session creation/continuity, normalized synchronous messages, request-to-session cancellation, optional in-memory HTTP basic authentication, and fail-closed streaming capability declaration. **Complete and CI-verified.**
- **Phase 24 — OmniRoute Integration:** stdlib-only OpenAI-compatible gateway client, deterministic model discovery, fail-closed health checks, secure credential handling, retryable transport classification, session/idempotency/request correlation forwarding, and a governed invocation layer that delegates provider/model routing to OmniRoute. **Complete and CI-verified.**
- **Phase 25 — Termux Runtime:** vendor-neutral environment readiness contracts, Termux detection, Python/Git/curl/OpenSSH/pkg checks, OpenCode readiness, optional fail-closed OmniRoute health, read-only Termux doctor, secret-free JSON reporting, conservative package planning, and workspace validation. **Complete and CI-verified.**
- **Phase 26 — GitHub Codespaces Runtime:** Codespaces detection, Python/Git/curl/OpenSSH/workspace checks, OpenCode readiness, optional GitHub CLI and OmniRoute requirements, read-only toolchain planning, workspace validation, and secret-free doctor reporting. **Complete and CI-verified.**
- **Phase 27 — `si` CLI + Easy Setup:** user-facing doctor/status/agents/teams/setup/update/run commands, non-secret configuration, explicit mutation gates, safe OpenCode OmniRoute configuration, governed team execution, packaged canonical catalogs, and wheel-level CLI verification. **Complete and CI-verified.**
- **Phase 28 — Cross-environment & Handoff:** portable `si.handoff.v1` workflow envelopes, SHA-256 integrity verification, secret rejection, sanitized project identity, explicit Termux↔Codespaces import/export validation, resumable workflow context, atomic handoff storage, and CLI handoff commands. **Complete and CI-verified.**
- **Phase 29 — Agent Persona & Definition System:** deterministic Markdown personas, typed behavioral contracts, validation, governed compilation, duplicate/conflict detection, canonical persona set, provenance, inert/untrusted persona handling, and packaged persona artifacts. **Complete and CI-verified.**

## `si` CLI

```text
si doctor [--json]
si status
si agents
si teams
si setup [--apply] [--configure-opencode] [--model MODEL]
si update [--apply]
si run TEAM --objective TEXT [--handoff FILE]
si handoff create TEAM --objective TEXT --source termux|codespace --target termux|codespace --output FILE
si handoff inspect FILE
si handoff import FILE
```

`doctor`, `status`, `agents`, and `teams` are read-only. `setup` and `update` are dry-run by default and require `--apply` before mutation. Setup commands come from the existing environment runtime plan and are checked against an allowlist; arbitrary shell strings are rejected.

The CLI stores only non-secret configuration at `~/.config/si-agents/config.json` by default (or `SI_CONFIG`), using atomic replacement and restrictive permissions. No API key, password, provider credential, or OpenCode auth token is stored by SI-Agents.

With `si setup --configure-opencode --model <model> --apply`, the CLI can add/update an OmniRoute OpenAI-compatible provider in the current OpenCode JSON configuration. It refuses JSONC rather than rewriting it unsafely and requires an explicit model instead of guessing capabilities from OmniRoute's mixed `/v1/models` catalog.

`si run` executes canonical Phase 21 teams through the existing TeamEngine and worker/runtime governance. The optional `--handoff` input only restores validated workflow context; it does not grant permissions or bypass target-environment authorization.

### Cross-environment handoff

A handoff is an explicit portable JSON artifact. For example:

```text
si handoff create engineering-repair --objective "repair the failing build" --source termux --target codespace --output repair-handoff.json
si handoff inspect repair-handoff.json
si handoff import repair-handoff.json
si run engineering-repair --objective "continue the repair" --handoff repair-handoff.json
```

Handoffs preserve task state, workflow context, result summaries, checkpoints, and evidence references. They never contain credentials. Imports verify the SHA-256 integrity digest, target environment, and repository identity when available. No automatic file transfer, Git synchronization, credential migration, Codespace creation, or remote state service is introduced.

## Documentation

The maintained documentation entry points are:

- `docs/README.md` — documentation navigation and current baseline.
- `docs/architecture/README.md` — architecture navigation and historical phase index.
- `docs/architecture/PHASES.md` — authoritative current implementation/status and verification record.
- `docs/architecture/SI_AGENTS_V3.md` — forward roadmap for Phases 30–43.
- `docs/architecture/PHASE_1_FOUNDATION.md` — historical Phase 1 foundation record.

## Engineering loop

```text
OBSERVE → UNDERSTAND → RESEARCH → PLAN → EXECUTE → MEASURE
→ TEST → ATTACK THE SOLUTION → VERIFY → DOCUMENT → LEARN → GENERALIZE → REUSE
```

## Control and safety model

Agents, capabilities, tools, skills, knowledge, automation jobs, teams, harness adapters, environment runtimes, and handoff/persona artifacts are workers/data—not policy authorities. Registration or selection does not grant permission. High-risk actions remain approval-gated, repository mutation remains protected, and important claims require evidence.

Markdown personas are human-authored behavioral data. They are parsed and validated deterministically, compiled only against an existing typed `AgentDefinition`, and cannot add capabilities, permissions, tools, environments, harness access, commands, network access, credentials, or secrets.

OpenCode integration is a transport boundary, not a model/provider router. OpenCode owns its server, provider credentials, and harness lifecycle. SI-Agents sends normalized runtime requests and consumes normalized results. OmniRoute is the external model/provider routing authority for Phase 24 and remains so inside the Termux and Codespaces runtimes and Phase 27 CLI setup.

Phase 24 deliberately does not create a second provider-fallback or circuit-breaker system around OmniRoute. OmniRoute owns provider selection, upstream credentials, provider fallback, gateway-side quotas, routing policies, and provider circuit state. SI-Agents owns its invocation contract and fail-closed local governance boundaries.

Phase 25 and Phase 26 provide read-only environment readiness. Phase 27 is the first explicit mutation layer: setup/update actions require `--apply`, execution is allowlisted, credentials are not persisted, and OpenCode configuration is changed only through a narrow, parse-safe provider configuration path.

Phase 28 adds explicit state transfer but not state authority. Handoff import is validation plus context restoration; the target environment, target workspace, target harness, and existing governance remain authoritative. A handoff cannot enable a harness, grant a permission, execute an imported command, or migrate credentials.

Universal harness deployment is descriptive, not authoritative. A deployment manifest can describe agents, teams, skills, required permissions, and capabilities for a harness, but it cannot enable the harness, grant permissions, execute workers, or bypass governance. Vendor-specific adapters remain separate from the core.

## Next phase

**Phase 30 — First-Class Portable Skills** is the next implementation phase. It begins only from the verified Phase 29 baseline and synchronized documentation set.
