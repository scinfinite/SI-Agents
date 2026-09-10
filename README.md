# SI-Agents

SI-Agents is an evidence-driven AI engineering system designed to inspect software, diagnose problems, execute controlled changes, verify results, and learn reusable engineering patterns.

## Current status

**Post-v2 evolution — Phases 19–30 implemented and CI-verified; Phase 31 implementation complete pending final mainline CI.**

Phase 29 provides the complete SI-native specialist persona layer: **279 Markdown personas across 18 SI-owned domain divisions**, with typed catalog parity, deterministic parsing/validation, security boundaries, provenance separation, package coverage, and CI verification.

Phase 30 provides six canonical portable `SKILL.md` artifacts with deterministic parsing/validation, dependency-aware composition, SHA-256 manifests, explicit permission/verification gates, CLI integration, packaging, and regression coverage.

Phase 31 adds explicit Rules, Hooks, and Events: immutable bounded lifecycle events, deterministic declarative Rules, bounded in-process Hooks, fail-closed dangerous-operation handling, Skill lifecycle event integration, and adversarial regression tests. Rules and Hooks never grant permissions or execution authority.

## Completed phases

Phases 1–30 are complete as documented in `docs/architecture/PHASES.md`. Phase 31 is implementation-complete and remains gated only on final mainline CI evidence.

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
```

Read-only commands do not mutate state. Mutation requires explicit `--apply`. Credentials are not stored by SI-Agents. See `docs/architecture/CLI.md` for command behavior and safety invariants.

## Documentation

- `docs/README.md` — documentation navigation and current baseline.
- `docs/architecture/README.md` — architecture navigation and phase index.
- `docs/architecture/PHASES.md` — authoritative implementation/status and verification record.
- `docs/architecture/PHASE_29.md` — canonical Phase 29 persona/parity/provenance/security/packaging record.
- `docs/architecture/PHASE_30.md` — canonical Phase 30 portable Skill contract and verification record.
- `docs/architecture/PHASE_31.md` — canonical Phase 31 Rules/Hooks/Events contract and verification record.
- `docs/architecture/CLI.md` — current SI CLI surface, behavior, and safety model.
- `docs/architecture/SI_AGENTS_V3.md` — forward roadmap for Phases 30–43.

Historical phase records preserve their phase-time evidence; current state belongs in `PHASES.md` and the relevant current phase record.

## Engineering loop

```text
OBSERVE → UNDERSTAND → RESEARCH → PLAN → EXECUTE → MEASURE
→ TEST → ATTACK THE SOLUTION → VERIFY → DOCUMENT → LEARN → GENERALIZE → REUSE
```

## Control and safety model

Agents, capabilities, tools, skills, rules, hooks, events, knowledge, automation jobs, teams, harness adapters, environment runtimes, and persona artifacts are workers/data—not policy authorities. Registration or selection does not grant permission. High-risk actions remain approval-gated and important claims require evidence.

OpenCode is a transport/harness boundary. OmniRoute remains the model/provider routing authority. SI-Agents does not recreate provider fallback, quota, pricing, or circuit-breaker ownership.

Cross-environment handoffs transfer validated state as data only. They cannot grant permissions, migrate credentials, enable harnesses, execute imported commands, or bypass target-environment governance.

## Verification baseline

Phase 30 was merged to `main` as `62972acf20a0da53bf81161c2108a506dbdad907`, and mainline CI run **#727** passed successfully. Phase 31's final mainline CI is the remaining exit gate.

## Next phase

**Phase 32 — Memory & Knowledge** begins only after Phase 31's final mainline CI verification is green.
