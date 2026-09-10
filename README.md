# SI-Agents

SI-Agents is an evidence-driven AI engineering system designed to inspect software, diagnose problems, execute controlled changes, verify results, and learn reusable engineering patterns.

## Current status

**Post-v2 evolution — Phases 19–39 complete and CI-verified.**

The verified v3 foundation now includes 279 SI-native specialist personas across 18 divisions, portable Skills, Rules/Hooks/Events, scoped Memory/Knowledge, Security/Governance, organization teams/workflows, Control API v1, a localhost-first Web foundation, the live Control Center, interactive visual organization/workflow inspection, and a governed Agent Builder/customization boundary.

### Phase 39 — Agent Builder & Customization

Phase 39 adds a dependency-free local Agent Builder at `/agent-builder`. Operators can load a canonical agent into an editable draft, create new drafts, validate them, save revisions, run non-executing tests, archive drafts, and inspect deterministic Markdown previews.

Authority-bearing fields are fail-closed: new agents cannot self-grant capabilities, permissions, harnesses, or environments, while customizations cannot add those authorities or change canonical identity/division. Drafts are stored atomically in `.si/agent-builder.json`; the Builder never mutates the canonical catalog and never executes agents, tools, workflows, shell commands, harnesses, or external calls.

## Architecture

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

There is one SI Core and one Control API. Operator surfaces are views/boundaries, not independent authorities. `POST /api/v1/runs` remains governance-gated and creates a queued control record only.

## Security model

Agents, capabilities, tools, Skills, Rules, Hooks, events, memory, knowledge, automation, teams, harness adapters, environments, persona artifacts, and Builder drafts are workers/data—not policy authorities. Registration or selection does not grant permission. High-risk operations remain approval-gated and important claims require evidence.

The Web server is dependency-free and localhost-first. Remote exposure is explicit and authenticated, CORS is allowlisted, JSON mutation bodies are bounded, security headers are restrictive, audit data is redacted, and telemetry is not introduced. The Agent Builder adds no execution engine, external scripts, CDN dependencies, inline script/style, or persistent browser credentials.

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

Read-only commands do not mutate state. Mutation requires explicit `--apply` where applicable. Credentials are not stored by SI-Agents.

## Documentation

- `docs/README.md` — documentation navigation and current baseline.
- `docs/architecture/README.md` — architecture navigation and phase index through Phase 39.
- `docs/architecture/PHASES.md` — authoritative implementation/status and verification record.
- `docs/architecture/PHASE_29_AGENT_PERSONA.md` through `PHASE_39_AGENT_BUILDER.md` — canonical post-v2 phase records.
- `docs/architecture/SI_AGENTS_V3.md` — forward roadmap for Phases 40–43.

## Engineering loop

```text
OBSERVE → UNDERSTAND → RESEARCH → PLAN → EXECUTE → MEASURE
→ TEST → ATTACK THE SOLUTION → VERIFY → DOCUMENT → LEARN → GENERALIZE → REUSE
```

## Verification baseline

Phase 38 implementation merged as `657530eefa41794fb425cd0fe38d2aced9bd316d`; mainline CI **#845** (`34508914827`) passed all build, packaging, audit, Ruff, test, diagnostics, and cleanup gates. Phase 39 implementation merged from PR #38 as `22c381e23c6efb2e2eaa1819e975f308fcf3ff73`; feature CI **#853** (`34511009965`) passed all repository gates. The final documentation-closed mainline CI is recorded in the Phase 39 closure update.

## Next phase

**Phase 40 — Evidence & Observability.**
