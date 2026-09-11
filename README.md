# SI-Agents

SI-Agents is an evidence-driven AI engineering system designed to inspect software, diagnose problems, execute controlled changes, verify results, and learn reusable engineering patterns.

## Current status

**Post-v2 evolution — Phases 19–41 complete and CI-verified.**

The verified v3 foundation now includes 279 SI-native specialist personas across 18 divisions, portable Skills, Rules/Hooks/Events, scoped Memory/Knowledge, Security/Governance, organization teams/workflows, Control API v1, a localhost-first Web foundation, the live Control Center, visual organization/workflow inspection, a governed Agent Builder/customization boundary, evidence-first observability, and a first-class terminal operator interface.

### Phase 41 — SI TUI

Phase 41 adds a dependency-free, keyboard-first terminal operator surface for Termux, Codespaces, SSH, and ordinary terminals. It reads the same `ControlApiService` authority used by Web and exposes Overview, Agents, Teams, Workflows, Skills, Memory, Knowledge, Evidence, Runs, Organization, Governance, Environments, Harnesses, and Settings.

Navigation, filtering, selection, and refresh are local UI state only. `--once` supports deterministic non-interactive output; `NO_COLOR` and `--no-color` suppress terminal control behavior. The TUI cannot execute agents, tools, Skills, workflows, shells, harnesses, or governance mutations.

## Architecture

```text
CLI / TUI / Web Control Center / Harness
                 ↓
            Control API v1
                 ↓
           SI Core authorities
                 ↓
       Runtime / Governance / Evidence
                 ↓
             Harness boundary
```

There is one SI Core and one Control API. Operator surfaces are views/boundaries, not independent authorities.

## Security model

Agents, capabilities, tools, Skills, Rules, Hooks, events, memory, knowledge, automation, teams, harness adapters, environments, persona artifacts, Builder drafts, evidence records, and UI state are workers/data—not policy authorities. Registration or selection does not grant permission. High-risk operations remain approval-gated and evidence/verification state remains explicit.

The Web and TUI use no third-party runtime dependencies. Web remains localhost-first with explicit authenticated remote opt-in, bounded JSON mutations, restrictive security headers, redacted audit logging, and no telemetry. TUI has no mutation transport or credential persistence.

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
si tui [--root PATH] [--view VIEW] [--filter TEXT] [--once] [--no-color]
```

Read-only commands do not mutate state. Mutation requires explicit `--apply` where applicable. Credentials are not stored by SI-Agents.

## Documentation

- `docs/README.md` — documentation navigation and current baseline.
- `docs/architecture/README.md` — architecture navigation and phase index through Phase 41.
- `docs/architecture/PHASES.md` — authoritative implementation/status and verification record.
- `docs/architecture/PHASE_29_AGENT_PERSONA.md` through `PHASE_41_TUI.md` — canonical post-v2 phase records.
- `docs/architecture/SI_AGENTS_V3.md` — forward roadmap for Phases 42–43.

## Engineering loop

```text
OBSERVE → UNDERSTAND → RESEARCH → PLAN → EXECUTE → MEASURE
→ TEST → ATTACK THE SOLUTION → VERIFY → DOCUMENT → LEARN → GENERALIZE → REUSE
```

## Verification baseline

Phase 40 final mainline CI **#864** (`34513486696`) was green with 458 tests passed. Phase 41 implementation merged from PR #43 as `531d2b964a6567aaa0a6b34b2d9b8f4471eb83f5`; feature CI **#865** (`34553393908`) and post-merge mainline CI **#866** (`34553461275`) passed all repository gates. The final documentation-closed mainline verification is recorded in the Phase 41 closure update.

## Next phase

**Phase 42 — Harness Deployment Center.**
