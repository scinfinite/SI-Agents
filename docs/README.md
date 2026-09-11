# SI-Agents Documentation

This directory is the maintained documentation surface for SI-Agents. Documentation is organized so operators can distinguish **current truth**, **historical implementation records**, **post-v3 maintenance direction**, and **governance/policy**.

## Start here

1. **Project overview:** `../README.md`
2. **Current phase/status:** `architecture/PHASES.md`
3. **Architecture index:** `architecture/README.md`
4. **Phase 29 canonical record:** `architecture/PHASE_29_AGENT_PERSONA.md`
5. **Phase 30 canonical record:** `architecture/PHASE_30_PORTABLE_SKILLS.md`
6. **Phase 31 canonical record:** `architecture/PHASE_31_RULES_HOOKS_EVENTS.md`
7. **Phase 32 canonical record:** `architecture/PHASE_32_MEMORY_KNOWLEDGE.md`
8. **Phase 33 canonical record:** `architecture/PHASE_33_SECURITY_GOVERNANCE_CENTER.md`
9. **Phase 34 canonical record:** `architecture/PHASE_34_ORGANIZATION_EXPANSION.md`
10. **Phase 35 canonical record:** `architecture/PHASE_35_CONTROL_API.md`
11. **Phase 36 canonical record:** `architecture/PHASE_36_LOCAL_WEB_FOUNDATION.md`
12. **Phase 37 canonical record:** `architecture/PHASE_37_CONTROL_CENTER.md`
13. **Phase 38 canonical record:** `architecture/PHASE_38_VISUAL_ORGANIZATION_WORKFLOW.md`
14. **Phase 39 canonical record:** `architecture/PHASE_39_AGENT_BUILDER.md`
15. **Phase 40 canonical record:** `architecture/PHASE_40_EVIDENCE_OBSERVABILITY.md`
16. **Phase 41 canonical record:** `architecture/PHASE_41_TUI.md`
17. **Phase 42 canonical record:** `architecture/PHASE_42_HARNESS_DEPLOYMENT_CENTER.md`
18. **Phase 43 canonical record:** `architecture/PHASE_43_INTEGRATION_HARDENING.md`
19. **v3 architecture:** `architecture/SI_AGENTS_V3.md`
20. **Engineering rules:** `../AGENTS.md`
21. **IP/provenance policy:** `../governance/legal/IP_PROVENANCE.md`

## Source-of-truth rules

- `architecture/PHASES.md` is authoritative for current implementation status and verification.
- `architecture/README.md` is the maintained architecture navigation/index.
- `PHASE_29_AGENT_PERSONA.md` through `PHASE_43_INTEGRATION_HARDENING.md` are canonical records for their respective post-v2 phases.
- `SI_AGENTS_V3.md` records the completed v3 architecture and post-v3 direction.
- Earlier `PHASE_<n>_*.md` files are historical implementation records and preserve phase-time evidence.
- Runtime, governance, executable contracts, and CI results remain authoritative over prose.
- Documentation status must never outrun implementation or CI evidence.

## Documentation lifecycle

When a maintenance change changes an implementation contract: implement and test; run CI; record verified results in the current status/phase record when relevant; update navigation/root documentation; preserve historical evidence.

## Security and provenance

Markdown is documentation/configuration, not an authority boundary. Imported or externally inspired content must not silently grant permissions or execute code. Material design influence must follow the project's provenance policy and be independently implemented.

## Current baseline

**Phases 1–43 are complete and CI-verified.** Phase 43 implementation merged through the final correction as `52588921c0956f091fb569c4b51e9fd741790744`. Final mainline CI **#886** (`34558002476`) passed distribution, wheel installation, repository audit, Ruff, and the complete pytest suite.

**v3 implementation is closed.** Subsequent work is maintenance or explicitly versioned post-v3 evolution.
