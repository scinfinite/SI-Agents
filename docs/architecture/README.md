# SI-Agents Architecture Documentation

## Authority order

Use these documents in this order when determining project state:

1. **`PHASES.md`** — current implementation status and verification evidence.
2. **`SI_AGENTS_V3.md`** — future architecture and Phase 29–43 roadmap.
3. **Detailed phase documents** — historical contracts, boundaries, and completion evidence.
4. **`FOUNDATION.md` / `CONTROL_PLANE.md` / `EXECUTION_BACKENDS.md`** — cross-cutting architectural boundaries.

Code, executable contracts, governance decisions, and CI results outrank documentation when they conflict; the conflict must then be documented and corrected.

## Historical phase index

| Phase | Document | State |
|---:|---|---|
| 2 | `PHASE_2_CONTROL_PLANE.md` | Complete |
| 3 | `PHASE_3_TOOL_SYSTEM.md` | Complete |
| 4 | `PHASE_4_ENGINEERING_BRAIN.md` | Complete |
| 5 | `PHASE_5_DEVELOPER_DEBUGGER_TESTER.md` | Complete |
| 6 | `PHASE_6_SKILLS_ENGINE.md` | Complete |
| 7 | `PHASE_7_VERIFICATION_EVIDENCE.md` | Complete |
| 8 | `PHASE_8_TECHNICAL_KNOWLEDGE.md` | Complete |
| 9 | `PHASE_9_TECHNOLOGY_DISCOVERY.md` | Complete |
| 10 | `PHASE_10_OPEN_SOURCE_INTELLIGENCE.md` | Complete |
| 11 | `PHASE_11_PATTERN_EXTRACTION.md` | Complete |
| 12 | `PHASE_12_ENGINEERING_MEMORY.md` | Complete |
| 13 | `PHASE_13_SECURITY_LEGAL_COST.md` | Complete |
| 14 | `PHASE_14_MODEL_PROVIDER_INTELLIGENCE.md` | Complete |
| 15 | `PHASE_15_AUTOMATION.md` | Complete |
| 16 | `PHASE_16_CONTROLLED_SELF_IMPROVEMENT.md` | Complete |
| 17 | `PHASE_17_HARNESS_RUNTIME_INTEROPERABILITY.md` | Complete |
| 18 | `PHASE_18_PRODUCTION_HARDENING.md` | Complete |
| 19 | `PHASE_19_REALITY_AUDIT.md` | Complete |
| 20 | `PHASE_20_AGENT_ORGANIZATION.md` | Complete |
| 21 | `PHASE_21_AGENT_TEAMS_WORKFLOWS.md` | Complete |
| 22 | `PHASE_22_UNIVERSAL_HARNESS_INTEGRATION.md` | Complete |
| 23 | `PHASE_23_OPENCODE_INTEGRATION.md` | Complete |
| 24 | `PHASE_24_OMNIROUTE_INTEGRATION.md` | Complete |
| 25 | `PHASE_25_TERMUX_RUNTIME.md` | Complete |
| 26 | `PHASE_26_CODESPACE_RUNTIME.md` | Complete |
| 27 | `PHASE_27_SI_CLI.md` | Complete |
| 28 | `PHASE_28_CROSS_ENVIRONMENT_HANDOFF.md` | Complete + CI verified |

Phase 1 is represented by `FOUNDATION.md` and the repository-level engineering/governance documents rather than a `PHASE_1_*.md` file.

## Cross-cutting architecture

- `FOUNDATION.md` — project principles and foundational boundaries.
- `CONTROL_PLANE.md` — orchestration/control-plane contracts.
- `EXECUTION_BACKENDS.md` — execution backend separation.
- `PHASE_17_HARNESS_RUNTIME_INTEROPERABILITY.md` — vendor-neutral runtime boundary.
- `PHASE_22_UNIVERSAL_HARNESS_INTEGRATION.md` — language-neutral harness contract.
- `PHASE_24_OMNIROUTE_INTEGRATION.md` — model/provider delegation boundary.
- `PHASE_28_CROSS_ENVIRONMENT_HANDOFF.md` — portable state-transfer boundary.

## v3 roadmap

`SI_AGENTS_V3.md` defines Phases 29–43. The implementation order is intentionally layered:

```text
29 Personas
   ↓
30 Skills
   ↓
31 Rules / Hooks / Events
   ↓
32 Memory / Knowledge
   ↓
33 Governance Center
   ↓
34 Organization Expansion
   ↓
35 Control API
   ↓
36 Web Foundation
   ↓
37 Control Center
   ↓
38 Visual Organization / Workflow
   ↓
39 Agent Builder
   ↓
40 Evidence / Observability
   ↓
41 TUI
   ↓
42 Harness Deployment Center
   ↓
43 Integration / Hardening
```

The Web and TUI are operator surfaces over one SI Core and one Control API; they must not become independent authorities.

## Documentation maintenance

Do not rewrite completed phase documents merely to reflect later phases. Put current status and cross-phase changes in `PHASES.md`, and put future work in `SI_AGENTS_V3.md`. Any material implementation or verification change must update the appropriate status/evidence record.
