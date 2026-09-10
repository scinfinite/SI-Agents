# SI-Agents

SI-Agents is an evidence-driven AI engineering system designed to inspect software, diagnose problems, execute controlled changes, verify results, and learn reusable engineering patterns.

## Current status

**Post-v2 evolution — Phases 19–29 implemented and CI-verified.**

Phase 29 now provides the complete SI-native specialist persona layer: **279 Markdown personas across 18 SI-owned domain divisions**, with typed catalog parity, deterministic parsing/validation, security boundaries, provenance separation, package coverage, and CI verification.

The canonical Phase 29 record is `docs/architecture/PHASE_29.md`. Phase 29 uses SI-specific persona identifiers and directory names; the canonical persona corpus is the Markdown hierarchy under `agents/si-*/`.

## Completed phases

Phases 1–28 remain complete as documented in `docs/architecture/PHASES.md`. Phase 29 completes the specialist persona and definition layer on top of the existing typed organization, workflow, governance, runtime, harness, model-routing, CLI, and handoff architecture.

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

Read-only commands do not mutate state. Mutation requires explicit `--apply`. Credentials are not stored by SI-Agents.

## Documentation

- `docs/README.md` — documentation navigation and current baseline.
- `docs/architecture/README.md` — architecture navigation and phase index.
- `docs/architecture/PHASES.md` — authoritative implementation/status and verification record.
- `docs/architecture/PHASE_29.md` — single canonical Phase 29 persona/parity/provenance/security/packaging record.
- `docs/architecture/SI_AGENTS_V3.md` — forward roadmap for Phases 30–43.

Historical phase records preserve their phase-time evidence; current state belongs in `PHASES.md` and the relevant current phase record.

## Engineering loop

```text
OBSERVE → UNDERSTAND → RESEARCH → PLAN → EXECUTE → MEASURE
→ TEST → ATTACK THE SOLUTION → VERIFY → DOCUMENT → LEARN → GENERALIZE → REUSE
```

## Control and safety model

Agents, capabilities, tools, skills, knowledge, automation jobs, teams, harness adapters, environment runtimes, and persona artifacts are workers/data—not policy authorities. Registration or selection does not grant permission. High-risk actions remain approval-gated and important claims require evidence.

OpenCode is a transport/harness boundary. OmniRoute remains the model/provider routing authority. SI-Agents does not recreate provider fallback, quota, pricing, or circuit-breaker ownership.

Cross-environment handoffs transfer validated state as data only. They cannot grant permissions, migrate credentials, enable harnesses, execute imported commands, or bypass target-environment governance.

## Verification baseline

The completed Phase 29 verification run recorded **358 tests passed**, successful distribution build, isolated wheel installation/import, CLI smoke checks, and Ruff. GitHub Actions uses Node 24-compatible `actions/checkout@v5` and `actions/setup-python@v6`.

## Next phase

**Phase 30 — First-Class Portable Skills** is the next implementation phase and begins from the verified Phase 29 baseline.
