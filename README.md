# SI-Agents

SI-Agents is an evidence-driven AI engineering system designed to inspect software, diagnose problems, execute controlled changes, verify results, and learn reusable engineering patterns.

## Current status

**Post-v2 evolution — Phases 19–37 complete and CI-verified.**

Phase 29 provides the complete SI-native specialist persona layer: **279 Markdown personas across 18 SI-owned domain divisions**, with typed catalog parity, deterministic parsing/validation, security boundaries, provenance separation, package coverage, and CI verification.

Phase 30 provides six canonical portable `SKILL.md` artifacts with deterministic parsing/validation, dependency-aware composition, SHA-256 manifests, explicit permission/verification gates, CLI integration, packaging, and regression coverage.

Phase 31 adds explicit Rules, Hooks, and Events: immutable bounded lifecycle events, deterministic declarative Rules, bounded in-process Hooks, fail-closed dangerous-operation handling, Skill lifecycle event integration, and adversarial regression tests. Rules and Hooks never grant permissions or execution authority.

Phase 32 adds scoped immutable Memory, verified source-backed Knowledge, provenance/evidence contracts, fail-closed promotion, explicit supersession/contradiction tracking, deterministic context-aware retrieval, atomic schema-versioned persistence, and lifecycle event integration.

Phase 33 adds typed Security/Governance contracts, fail-closed authorization, approval handling, external-egress controls, declarative governance configuration, deterministic security scanning, and audit-safe decisions.

Phase 34 adds five operating teams, 18 single-home division assignments, four evidence-gated organization workflows, source-of-truth validation against the 279-agent catalog, and authority-boundary checks.

Phase 35 adds the stable machine-facing **Control API v1**, deterministic OpenAPI description, canonical organization/runtime read models, governed run submission, localhost-only dependency-free HTTP transport, bounded JSON mutation input, and the packaged `si-api` launcher.

Phase 36 adds the dependency-free **local Web foundation**, packaged browser assets, stable `si web`/`si-web` launchers, strict CSP/security headers, deny-by-default CORS, explicit authenticated remote opt-in, bounded JSON mutations, redacted private audit logging, safe errors, and graceful shutdown.

Phase 37 adds the live **Control Center** over the Control API: Overview, Agents, Teams, Workflows, Skills, Memory, Knowledge, Evidence, Runs, Organization, Governance, Environments, Harnesses, and Settings views, plus sanitized read-model extensions and browser/read-model security regression coverage.

## Completed phases

**Phases 1–37 are complete and CI-verified.** Phase 36 feature CI **#830** (`34505281056`) passed with **434 tests**, followed by final mainline CI **#833** (`34505742175`) on commit `f76717fa11f1ce275e0459724f6e6e871b4d1922`. Phase 37 final mainline CI **#840** (`34507154878`) passed all repository gates on commit `d54ab5a0e9a0dc5daed72e89bdaf842b8da59078`, with **441 tests passed**.

## Control Center and Control API

```text
CLI / Web Control Center / TUI / Harness
                    ↓
               Control API v1
                    ↓
             SI Core authorities
       ┌────────────┼─────────────┐
    Agents       Organization   Governance
    Skills       Memory         Verification
```

The Control Center is a presentation/operator surface, not a second control plane. All browser data is read from the canonical Control API. `POST /api/v1/runs` remains governance-gated and creates a queued record only; it never executes an agent, Skill, workflow, tool, shell command, or external request.

Phase 36's dependency-free Web server remains localhost-first. Remote exposure is explicit and authenticated, CORS is allowlisted, request bodies are bounded, security headers are restrictive, audit data is redacted, and no telemetry is introduced. Phase 37 adds no browser-side execution engine or persistent browser credential storage.

## SI Agent Persona System

```text
agents/
├── base.py / developer.py / debugger.py / tester.py   # runtime/model compatibility
├── si-cognition/
├── si-creative/
├── si-delivery/
├── si-engineering/
├── si-finance/
├── si-game/
├── si-geospatial/
├── si-growth/
├── si-health/
├── si-market/
├── si-product/
├── si-research/
├── si-revenue/
├── si-security/
├── si-spatial/
├── si-specialized/
├── si-support/
└── si-verification/
```

The 18 SI-owned directories contain exactly 279 canonical Markdown persona definitions. Every persona has an SI-specific ID, name, filename, and division. The four top-level Python modules are compatibility/model modules and are not counted as persona definitions.

Persona Markdown is behavioral data only. It cannot grant permissions, tools, credentials, environments, harness access, commands, network access, or execution authority. Typed `AgentDefinition` contracts remain authoritative.

## Rules, Hooks & Events

```text
Agent / Skill / Tool / Workflow / Runtime / Handoff / Verification
                             ↓
                          EventBus
                        ↙         ↘
                    Rules         Hooks
                      ↓              ↓
                policy signal   bounded lifecycle
                      ↘              ↙
                    existing governance
```

The canonical Rule catalog is `config/rules.v1.json`. Events are immutable, size-bounded, and secret-like payload keys are redacted. Hooks are explicit in-process registrations; arbitrary shell/command hooks are not supported. Dangerous events fail closed without a matching Rule, and gate-hook failures fail closed.

## Memory & Knowledge

```text
Observation
    ↓
Candidate Memory → evidence → validation → scoped promotion
    ↓                              ↓
Task → Project → Team → Agent → Division → Organization → Global

Verified source-backed Knowledge
    ↓
explicit evidence + provenance + confidence
    ↓
deterministic retrieval (never proof or authorization)
```

Memory records provenance, evidence, confidence, lifecycle, expiry, supersession, contradictions, scope identity, and version. Knowledge requires verified evidence. Persistence uses schema-versioned atomic JSON writes and rejects unknown/malformed stores rather than silently resetting them.

## `si` CLI

```text
si doctor [--json]
si status [--json]
si audit [--json]
si agents [--division DIVISION] [--status STATUS] [--search TEXT] [--json]
si personas [--division DIVISION] [--search TEXT] [--json]
si teams [--search TEXT] [--json]
si setup [--apply] [--install-opencode] [--configure-opencode] [--model MODEL]
si update [--apply]
si run TEAM --objective TEXT [--handoff FILE]
si handoff create TEAM --objective TEXT --source termux|codespace --target termux|codespace --output FILE
si handoff inspect FILE [--json]
si handoff import FILE
si web [--host HOST] [--port PORT] [--root PATH] [--allow-remote]
```

Read-only commands do not mutate state. Mutation requires explicit `--apply` where applicable. Credentials are not stored by SI-Agents. See `docs/architecture/CLI.md` for command behavior and safety invariants.

## Documentation

- `docs/README.md` — documentation navigation and current baseline.
- `docs/architecture/README.md` — architecture navigation and phase index through Phase 37.
- `docs/architecture/PHASES.md` — authoritative implementation/status and verification record.
- `docs/architecture/PHASE_29_AGENT_PERSONA.md` — canonical Phase 29 persona/parity/provenance/security/packaging record.
- `docs/architecture/PHASE_30_PORTABLE_SKILLS.md` — canonical Phase 30 portable Skill contract and verification record.
- `docs/architecture/PHASE_31_RULES_HOOKS_EVENTS.md` — canonical Phase 31 Rules/Hooks/Events contract and verification record.
- `docs/architecture/PHASE_32_MEMORY_KNOWLEDGE.md` — canonical Phase 32 Memory/Knowledge contract and final verification record.
- `docs/architecture/PHASE_33_SECURITY_GOVERNANCE_CENTER.md` — canonical Phase 33 Security/Governance contract and final verification record.
- `docs/architecture/PHASE_34_ORGANIZATION_EXPANSION.md` — canonical Phase 34 Organization Expansion contract and final verification record.
- `docs/architecture/PHASE_35_CONTROL_API.md` — canonical Phase 35 Control API contract and final verification record.
- `docs/architecture/PHASE_36_LOCAL_WEB_FOUNDATION.md` — canonical Phase 36 Web foundation contract and final verification record.
- `docs/architecture/PHASE_37_CONTROL_CENTER.md` — canonical Phase 37 Control Center contract and final verification record.
- `docs/architecture/CLI.md` — current SI CLI surface, behavior, and safety model.
- `docs/architecture/SI_AGENTS_V3.md` — forward roadmap for remaining Phases 38–43.

Historical phase records preserve their phase-time evidence; current state belongs in `PHASES.md` and the relevant current phase record.

## Engineering loop

```text
OBSERVE → UNDERSTAND → RESEARCH → PLAN → EXECUTE → MEASURE
→ TEST → ATTACK THE SOLUTION → VERIFY → DOCUMENT → LEARN → GENERALIZE → REUSE
```

## Control and safety model

Agents, capabilities, tools, skills, rules, hooks, events, knowledge, memory, automation jobs, teams, harness adapters, environment runtimes, and persona artifacts are workers/data—not policy authorities. Registration or selection does not grant permission. High-risk actions remain approval-gated and important claims require evidence.

OpenCode is a transport/harness boundary. OmniRoute remains the model/provider routing authority. SI-Agents does not recreate provider fallback, quota, pricing, or circuit-breaker ownership.

Cross-environment handoffs transfer validated state as data only. They cannot grant permissions, migrate credentials, enable harnesses, execute imported commands, or bypass target-environment governance.

The Control API and Web Control Center are operator/harness boundaries over the same SI Core. They do not create a second authority or execution engine.

## Verification baseline

Phase 30 was merged to `main` as `62972acf20a0da53bf81161c2108a506dbdad907`, and mainline CI run **#727** passed successfully. Phase 31 was merged as `32db86c560053e831b0740c5614d63bf64d3ce6b` after final CI run **#735** passed on the exact Phase 31 source tree. Phase 32 feature CI run **#762** passed, followed by mainline CI run **#769**, which passed repository audit, Ruff, distribution/wheel checks, and the full test suite (**392 passed in 5.47s**). Phase 33 feature CI **#785** passed with 402 tests and mainline CI **#786** passed on the implementation merge. Phase 34 feature CI **#798** passed with 409 tests and mainline CI **#799** passed on the implementation merge. Phase 35 feature CI **#809** passed all gates with 417 tests. Phase 36 feature CI **#830** passed all gates with 434 tests and final mainline CI **#833** passed on `f76717fa11f1ce275e0459724f6e6e871b4d1922`. Phase 37 final mainline CI **#840** passed all gates on `d54ab5a0e9a0dc5daed72e89bdaf842b8da59078` with **441 tests passed**.

## Next phase

**Phase 38 — Visual Organization & Workflow.**
