# SI-Agents Architecture Documentation

## Authority order

1. `PHASES.md` — current implementation status and verification evidence.
2. `SI_AGENTS_V3.md` — forward architecture and post-v3 maintenance direction.
3. Detailed phase documents — historical contracts and phase evidence.
4. Cross-cutting contracts such as `PHASE_1_FOUNDATION.md`, `PHASE_2_CONTROL_PLANE.md`, and `EXECUTION_BACKENDS.md`.

Code, executable contracts, governance decisions, and CI results outrank prose when they conflict; the conflict must be corrected in documentation.

## Phase index

Phases **1–43 are complete and CI-verified**.

| Phase | Canonical/current record | State |
|---:|---|---|
| 1–28 | Historical `PHASE_<n>_*.md` records | Complete |
| 29 | `PHASE_29_AGENT_PERSONA.md` | Complete + CI verified |
| 30 | `PHASE_30_PORTABLE_SKILLS.md` | Complete + CI verified |
| 31 | `PHASE_31_RULES_HOOKS_EVENTS.md` | Complete + CI verified |
| 32 | `PHASE_32_MEMORY_KNOWLEDGE.md` | Complete + CI verified |
| 33 | `PHASE_33_SECURITY_GOVERNANCE_CENTER.md` | Complete + CI verified |
| 34 | `PHASE_34_ORGANIZATION_EXPANSION.md` | Complete + CI verified |
| 35 | `PHASE_35_CONTROL_API.md` | Complete + CI verified |
| 36 | `PHASE_36_LOCAL_WEB_FOUNDATION.md` | Complete + CI verified |
| 37 | `PHASE_37_CONTROL_CENTER.md` | Complete + CI verified |
| 38 | `PHASE_38_VISUAL_ORGANIZATION_WORKFLOW.md` | Complete + CI verified |
| 39 | `PHASE_39_AGENT_BUILDER.md` | Complete + CI verified |
| 40 | `PHASE_40_EVIDENCE_OBSERVABILITY.md` | Complete + CI verified |
| 41 | `PHASE_41_TUI.md` | Complete + CI verified |
| 42 | `PHASE_42_HARNESS_DEPLOYMENT_CENTER.md` | Complete + CI verified |
| 43 | `PHASE_43_INTEGRATION_HARDENING.md` | Complete + CI verified |

## Cross-cutting architecture

- One SI Core and one Control API are the authority boundaries.
- CLI, Web, and TUI are operator surfaces; they must not duplicate authorization or execution authority.
- Evidence is explicit and provenance-bearing; recording evidence does not make it automatically verified.
- Agent Builder is a governed authoring boundary, not an execution engine.
- The TUI is a terminal view over the same Control API service used by Web.
- Harness Deployment Center is a planning/deployment-description boundary; it does not grant permissions, migrate credentials, or execute harnesses.
- Final Integration Hardening is a verification boundary; it checks consistency but never executes downstream work.
- Harnesses remain downstream execution boundaries.

## v3 sequence

```text
29 Personas [complete]
 → 30 Skills [complete]
 → 31 Rules/Hooks/Events [complete]
 → 32 Memory/Knowledge [complete]
 → 33 Governance [complete]
 → 34 Organization [complete]
 → 35 Control API [complete]
 → 36 Web Foundation [complete]
 → 37 Control Center [complete]
 → 38 Visual Organization/Workflow [complete]
 → 39 Agent Builder [complete]
 → 40 Evidence/Observability [complete]
 → 41 TUI [complete]
 → 42 Harness Deployment Center [complete]
 → 43 Integration/Hardening [complete]
```

## Documentation maintenance

`PHASES.md` is authoritative for current status. `SI_AGENTS_V3.md` records the completed v3 architecture and post-v3 direction. Historical phase records preserve their phase-time evidence. New changes must update the current status/index documents without rewriting historical claims.
