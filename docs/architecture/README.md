# SI-Agents Architecture Documentation

## Authority order

Use these documents in this order when determining project state:

1. **`PHASES.md`** — current implementation status and verification evidence.
2. **`SI_AGENTS_V3.md`** — future architecture and Phase 30–43 roadmap after Phase 29 completion.
3. **Detailed phase documents** — historical contracts, boundaries, and completion evidence.
4. **`PHASE_1_FOUNDATION.md` / `EXECUTION_BACKENDS.md`** — cross-cutting architectural boundaries; the Phase 2 control-plane contract is consolidated into `PHASE_2_CONTROL_PLANE.md`.

Code, executable contracts, governance decisions, and CI results outrank documentation when they conflict; the conflict must then be documented and corrected.

## Historical phase index

| Phase | Document | State |
|---:|---|---|
| 1 | `PHASE_1_FOUNDATION.md` | Complete |
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
| 29 | `PHASE_29.md` | Complete + CI verified |
| 30 | `PHASE_30.md` | Complete + CI verified |
| 31 | `PHASE_31.md` | Complete + CI verified |

## Cross-cutting architecture

- `PHASE_1_FOUNDATION.md` — project principles and foundational boundaries.
- `PHASE_2_CONTROL_PLANE.md` — consolidated orchestration, authorization, execution-record, checkpoint, evidence, and execution-backend control-plane contract.
- `EXECUTION_BACKENDS.md` — execution backend separation and trust-boundary limitations.
- `PHASE_17_HARNESS_RUNTIME_INTEROPERABILITY.md` — vendor-neutral runtime boundary.
- `PHASE_22_UNIVERSAL_HARNESS_INTEGRATION.md` — language-neutral harness contract.
- `PHASE_24_OMNIROUTE_INTEGRATION.md` — model/provider delegation boundary.
- `PHASE_28_CROSS_ENVIRONMENT_HANDOFF.md` — portable state-transfer boundary.
- `PHASE_29.md` — canonical SI persona, parity, provenance, security, packaging, and verification record.
- `PHASE_30.md` — canonical portable Skill contract and verification record.
- `PHASE_31.md` — canonical Rules/Hooks/Events contract and verification record.
- `CLI.md` — current SI CLI command surface, diagnostics, filtering, setup controls, and safety invariants.

## v3 roadmap

`SI_AGENTS_V3.md` defines the remaining **Phases 30–43**. Phases 29–31 are complete and CI-verified.

```text
29 SI Agent Personas       [complete]
   ↓
30 Skills                  [complete]
   ↓
31 Rules / Hooks / Events  [complete]
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

Historical phase documents preserve the phase-time implementation record. Current status and cross-phase changes belong in `PHASES.md`; future work belongs in `SI_AGENTS_V3.md`. When later phases materially affect a boundary, record the current implication in the authoritative status/index documents without rewriting history to claim that later functionality existed in the earlier phase.
