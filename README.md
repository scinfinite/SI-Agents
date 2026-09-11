# SI-Agents

SI-Agents is an evidence-driven AI engineering system designed to inspect software, diagnose problems, execute controlled changes, verify results, and learn reusable engineering patterns.

## Current status

**Post-v2 evolution — Phases 19–42 complete and CI-verified.**

The verified v3 foundation now includes 279 SI-native specialist personas across 18 divisions, portable Skills, Rules/Hooks/Events, scoped Memory/Knowledge, Security/Governance, organization teams/workflows, Control API v1, localhost-first Web, Control Center, visual organization/workflow inspection, Agent Builder, evidence-first observability, TUI, and the governed Harness Deployment Center.

### Phase 42 — Harness Deployment Center

Phase 42 adds a deterministic planning and inspection boundary for registered harness adapters. Deployment plans can be validated and can prepare existing portable deployment descriptions, but cannot grant authority, move credentials, enable adapters, execute workers, invoke tools/shells, or make external calls. Unknown targets and authority-bearing capability/permission requests fail closed.

The Web surface is available at `/deployments`; the API exposes `GET/POST /api/v1/deployments`; and the CLI exposes `si deploy` plus `si-deploy` for target/plan inspection and planning. There is intentionally no apply/deploy command in this phase.

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

There is one SI Core and one Control API. Operator surfaces and deployment planning are views/boundaries, not independent authorities.

## Security model

Agents, capabilities, tools, Skills, Rules, Hooks, events, memory, knowledge, automation, teams, harness adapters, environments, persona artifacts, Builder drafts, evidence records, deployment plans, and UI state are workers/data—not policy authorities. Registration or selection does not grant permission. High-risk operations remain approval-gated and evidence/verification state remains explicit.

Web/TUI/deployment surfaces use no third-party runtime dependencies. Web remains localhost-first with explicit authenticated remote opt-in, bounded JSON mutations, restrictive security headers, redacted audit logging, and no telemetry. Deployment planning has no credential persistence or execution transport.

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
```

Read-only commands do not mutate state. Mutation requires explicit `--apply` where applicable. Credentials are not stored by SI-Agents.

## Documentation

- `docs/README.md` — documentation navigation and current baseline.
- `docs/architecture/README.md` — architecture navigation and phase index through Phase 42.
- `docs/architecture/PHASES.md` — authoritative implementation/status and verification record.
- `docs/architecture/PHASE_29_AGENT_PERSONA.md` through `PHASE_42_HARNESS_DEPLOYMENT_CENTER.md` — canonical post-v2 phase records.
- `docs/architecture/SI_AGENTS_V3.md` — forward roadmap for Phase 43.

## Engineering loop

```text
OBSERVE → UNDERSTAND → RESEARCH → PLAN → EXECUTE → MEASURE
→ TEST → ATTACK THE SOLUTION → VERIFY → DOCUMENT → LEARN → GENERALIZE → REUSE
```

## Verification baseline

Phase 42 implementation merged through PR #46 as `70d5f96c15bfbf200804a50f43dc6e12f5dde903`. During validation, wheel installation caught an OpenAPI syntax regression; Ruff then caught compact-handler/test style violations; pytest caught duplicate normalization and an assertion mismatch. These issues were fixed and revalidated before merge. The documentation-closed mainline CI is the final Phase 42 closure gate.

## Next phase

**Phase 43 — Final v3 Integration & Hardening.**
