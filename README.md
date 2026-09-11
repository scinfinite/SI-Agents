# SI-Agents

SI-Agents is an evidence-driven AI engineering system designed to inspect software, diagnose problems, execute controlled changes, verify results, and learn reusable engineering patterns.

## Current status

**Post-v2 evolution — Phases 19–43 complete and CI-verified.**

The verified v3 foundation includes 279 SI-native specialist personas across 18 divisions, portable Skills, Rules/Hooks/Events, scoped Memory/Knowledge, Security/Governance, organization teams/workflows, Control API v1, localhost-first Web, Control Center, visual organization/workflow inspection, Agent Builder, evidence-first observability, TUI, the governed Harness Deployment Center, and final cross-cutting integration hardening.

### Phase 43 — Final v3 Integration & Hardening

Phase 43 adds a deterministic integration audit over the complete v3 surface and a packaged `si verify`/`si-verify` readiness command. It checks canonical catalog/config consistency, required operator surfaces, packaging entry points, deployment planning-only boundaries, and documentation status without executing downstream work.

The final hardening pass also removed the unused deployment `APPLIED` state, retained fail-closed release-gate semantics, and added adversarial regression coverage. A schema-version compatibility regression found by mainline CI was corrected before final closure.

## Architecture

```text
CLI / TUI / Web Control Center / Deployment Center / Harness
                         ↓
                    Control API v1
                         ↓
                   SI Core authorities
                         ↓
              Runtime / Governance / Evidence
                         ↓
                   Harness boundary
```

There is one SI Core and one Control API. Operator surfaces, deployment planning, and integration verification are boundaries, not independent authorities.

## Security model

Agents, capabilities, tools, Skills, Rules, Hooks, events, memory, knowledge, automation, teams, harness adapters, environments, persona artifacts, Builder drafts, evidence records, deployment plans, and UI state are workers/data—not policy authorities. Registration or selection does not grant permission. High-risk operations remain approval-gated and evidence/verification state remains explicit.

Web/TUI/deployment/verification surfaces use no third-party runtime dependencies. Web remains localhost-first with explicit authenticated remote opt-in, bounded JSON mutations, restrictive security headers, redacted audit logging, and no telemetry. Deployment planning has no credential persistence or execution transport. Integration verification has no downstream execution authority.

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
si deploy targets [--root PATH] [--json]
si deploy plans [--root PATH] [--json]
si deploy plan PLAN_ID HARNESS_ID [--root PATH] [--json]
si verify [--root PATH] [--json]
```

Read-only commands do not mutate state. Mutation requires explicit `--apply` where applicable. Credentials are not stored by SI-Agents.

## Documentation

- `docs/README.md` — documentation navigation and current baseline.
- `docs/architecture/README.md` — architecture navigation and phase index through Phase 43.
- `docs/architecture/PHASES.md` — authoritative implementation/status and verification record.
- `docs/architecture/PHASE_29_AGENT_PERSONA.md` through `PHASE_43_INTEGRATION_HARDENING.md` — canonical post-v2 phase records.
- `docs/architecture/SI_AGENTS_V3.md` — completed v3 architecture and post-v3 direction.

## Engineering loop

```text
OBSERVE → UNDERSTAND → RESEARCH → PLAN → EXECUTE → MEASURE
→ TEST → ATTACK THE SOLUTION → VERIFY → DOCUMENT → LEARN → GENERALIZE → REUSE
```

## Verification baseline

Phase 43 implementation merged as `d4aaddc0008d6af05161d8b79dfc1f9507e0c61e`. Mainline CI **#884** (`34557632059`) exposed a schema-version compatibility regression in the new integration audit; it was fixed through PR #50 and merged as `52588921c0956f091fb569c4b51e9fd741790744`. Final mainline CI **#886** (`34558002476`) passed all repository gates.

## v3 status

**The SI-Agents v3 implementation is complete.** Future changes are maintenance, security/defect fixes, or explicitly versioned post-v3 evolution.
