# SI-Agents

SI-Agents is an evidence-driven AI engineering system designed to inspect software, diagnose problems, execute controlled changes, verify results, and learn reusable engineering patterns.

## Current status

**Post-v2 evolution — Phases 19–38 complete and CI-verified.**

The verified v3 foundation now includes 279 SI-native specialist personas across 18 divisions, portable Skills, Rules/Hooks/Events, scoped Memory/Knowledge, Security/Governance, organization teams/workflows, Control API v1, a localhost-first Web foundation, the live Control Center, and interactive visual organization/workflow inspection.

### Phase 38 — Visual Organization & Workflow

Phase 38 adds a deterministic `/api/v1/visualization` read model and dependency-free SVG views for organizational topology (divisions → teams → agents), workflow topology (workflows → steps → assigned teams/agents and dependencies), Skills/capabilities/permission relationships, and current control-plane run state. Operators can filter nodes, inspect details, pan, zoom, reset, and use keyboard activation.

The browser remains read-only. Visualization never grants permissions, authorizes actions, executes agents/tools/workflows, or infers downstream execution progress.

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

Agents, capabilities, tools, Skills, Rules, Hooks, events, memory, knowledge, automation, teams, harness adapters, environments, and persona artifacts are workers/data—not policy authorities. Registration or selection does not grant permission. High-risk operations remain approval-gated and important claims require evidence.

The Web server is dependency-free and localhost-first. Remote exposure is explicit and authenticated, CORS is allowlisted, JSON mutation bodies are bounded, security headers are restrictive, audit data is redacted, and telemetry is not introduced. The Phase 38 visualization adds no browser execution engine, external scripts, CDN dependencies, inline script/style, or persistent browser credentials.

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
- `docs/architecture/README.md` — architecture navigation and phase index through Phase 38.
- `docs/architecture/PHASES.md` — authoritative implementation/status and verification record.
- `docs/architecture/PHASE_29_AGENT_PERSONA.md` through `PHASE_38_VISUAL_ORGANIZATION_WORKFLOW.md` — canonical post-v2 phase records.
- `docs/architecture/SI_AGENTS_V3.md` — forward roadmap for Phases 39–43.

## Engineering loop

```text
OBSERVE → UNDERSTAND → RESEARCH → PLAN → EXECUTE → MEASURE
→ TEST → ATTACK THE SOLUTION → VERIFY → DOCUMENT → LEARN → GENERALIZE → REUSE
```

## Verification baseline

Phase 37 final mainline CI **#840** (`34507154878`) passed all gates with **441 tests passed** on implementation commit `d54ab5a0e9a0dc5daed72e89bdaf842b8da59078`. Phase 38 implementation merged as `657530eefa41794fb425cd0fe38d2aced9bd316d`; mainline CI **#845** (`34508914827`) passed all build, packaging, audit, Ruff, test, diagnostics, and cleanup gates. Documentation closure merged as `b66528b73af795b29197d825c9f6b45219a57cee` and is subject to the final mainline CI gate for this exact current-state tree.

## Next phase

**Phase 39 — Agent Builder & Customization.**
