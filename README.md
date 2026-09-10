# SI-Agents

SI-Agents is an evidence-driven AI engineering system designed to inspect software, diagnose problems, execute controlled changes, verify results, and learn reusable engineering patterns.

## Current status

**Post-v2 evolution — Phases 19–40 complete and CI-verified.**

The verified v3 foundation now includes 279 SI-native specialist personas across 18 divisions, portable Skills, Rules/Hooks/Events, scoped Memory/Knowledge, Security/Governance, organization teams/workflows, Control API v1, a localhost-first Web foundation, the live Control Center, interactive visual organization/workflow inspection, a governed Agent Builder/customization boundary, and evidence-first observability.

### Phase 40 — Evidence & Observability

Phase 40 adds an explicit evidence boundary for recorded facts, observations, inferences, and uncertainties. Evidence carries provenance, source, confidence, verification state, optional run relationships, and supersession/contradiction state. Local evidence is persisted atomically under `.si/` with restrictive permissions.

The Control API exposes evidence records, detail, verification, and per-run timelines. A dependency-free Evidence Explorer is packaged at `/assets/evidence.html` and linked from the Control Center. Recording or inspecting evidence never executes agents, Skills, workflows, tools, shell commands, harnesses, or external calls.

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
                    ↓
            Evidence / Observability
```

There is one SI Core and one Control API. Operator surfaces are views/boundaries, not independent authorities. `POST /api/v1/runs` remains governance-gated and creates a queued control record only.

## Security model

Agents, capabilities, tools, Skills, Rules, Hooks, events, memory, knowledge, automation, teams, harness adapters, environments, persona artifacts, Builder drafts, and evidence records are workers/data—not policy authorities. Registration or selection does not grant permission. High-risk operations remain approval-gated and important claims require explicit evidence/verification state.

The Web server is dependency-free and localhost-first. Remote exposure is explicit and authenticated, CORS is allowlisted, JSON mutation bodies are bounded, security headers are restrictive, audit data is redacted, and telemetry is not introduced. The Agent Builder and Evidence Explorer add no execution engine, external scripts, CDN dependencies, inline script/style, or persistent browser credentials.

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
- `docs/architecture/README.md` — architecture navigation and phase index through Phase 40.
- `docs/architecture/PHASES.md` — authoritative implementation/status and verification record.
- `docs/architecture/PHASE_29_AGENT_PERSONA.md` through `PHASE_40_EVIDENCE_OBSERVABILITY.md` — canonical post-v2 phase records.
- `docs/architecture/SI_AGENTS_V3.md` — forward roadmap for Phases 41–43.

## Engineering loop

```text
OBSERVE → UNDERSTAND → RESEARCH → PLAN → EXECUTE → MEASURE
→ TEST → ATTACK THE SOLUTION → VERIFY → DOCUMENT → LEARN → GENERALIZE → REUSE
```

## Verification baseline

Phase 40 implementation merged from PR #40 as `2e363034f8140ea8ecc90cf7c0f2fe73`; mainline CI **#860** (`34512774276`) caught one evidence-route regression, fixed in PR #41 as `4900401c48af52a6e8d901b622575bc49bdab563`. Final mainline CI **#862** (`34513000130`) passed all build, packaging, audit, Ruff, test, diagnostics, and cleanup gates with **458 passed**.

## Next phase

**Phase 41 — TUI.**
