# SI-Agents Documentation

This directory is the maintained documentation surface for SI-Agents. Documentation is organized so operators can distinguish **current truth**, **historical implementation records**, **future roadmap**, and **governance/policy**.

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
16. **v3 roadmap (next work):** `architecture/SI_AGENTS_V3.md`
17. **Engineering rules:** `../AGENTS.md`
18. **IP/provenance policy:** `../governance/legal/IP_PROVENANCE.md`

## Documentation map

```text
docs/
├── README.md
└── architecture/
    ├── README.md
    ├── PHASES.md
    ├── PHASE_29_AGENT_PERSONA.md
    ├── PHASE_30_PORTABLE_SKILLS.md
    ├── PHASE_31_RULES_HOOKS_EVENTS.md
    ├── PHASE_32_MEMORY_KNOWLEDGE.md
    ├── PHASE_33_SECURITY_GOVERNANCE_CENTER.md
    ├── PHASE_34_ORGANIZATION_EXPANSION.md
    ├── PHASE_35_CONTROL_API.md
    ├── PHASE_36_LOCAL_WEB_FOUNDATION.md
    ├── PHASE_37_CONTROL_CENTER.md
    ├── PHASE_38_VISUAL_ORGANIZATION_WORKFLOW.md
    ├── PHASE_39_AGENT_BUILDER.md
    ├── PHASE_40_EVIDENCE_OBSERVABILITY.md
    ├── SI_AGENTS_V3.md
    ├── PHASE_1_FOUNDATION.md
    ├── EXECUTION_BACKENDS.md
    └── PHASE_<n>_*.md                         # Historical phase contracts/evidence
```

The former `FOUNDATION.md` and duplicate `CONTROL_PLANE.md` names have been retired. Phase 1 is explicitly indexed as `PHASE_1_FOUNDATION.md`, and the important control-plane execution contract is consolidated into `PHASE_2_CONTROL_PLANE.md`.

## Source-of-truth rules

- `PHASES.md` is authoritative for current implementation status and verification.
- `architecture/README.md` is the maintained architecture navigation/index.
- `PHASE_29_AGENT_PERSONA.md` through `PHASE_40_EVIDENCE_OBSERVABILITY.md` are canonical records for their respective post-v2 phases.
- `SI_AGENTS_V3.md` is authoritative for forward-looking v3 planning.
- Earlier `PHASE_<n>_*.md` files are historical implementation records and preserve phase-time evidence.
- Runtime, governance, executable contracts, and CI results remain authoritative over prose.
- Documentation status must never outrun implementation or CI evidence.

## Documentation lifecycle

When a phase changes state:

1. Implement and test the code.
2. Run the required CI gates.
3. Record the verified result in `PHASES.md` and the phase's canonical record.
4. Update root README and navigation indexes when public project state changes.
5. Keep future roadmap text separate from completed functionality.
6. Preserve historical phase evidence instead of rewriting history.

## Security and provenance

Markdown is documentation/configuration, not an authority boundary. Imported or externally inspired content must not silently grant permissions or execute code. Material design influence must follow the project's provenance policy and be independently implemented.

## Current baseline

**Phases 1–40 are complete and CI-verified.** Phase 40 implementation merged from PR #40 as `2e363034f8140ea8ecc90cf7c0f2fe73`; CI #860 caught one evidence-route regression, which was fixed in PR #41 as `4900401c48af52a6e8d901b622575bc49bdab563`. Final mainline CI **#862** (`34513000130`) passed all repository gates with **458 passed**.

**Next implementation: Phase 41 — TUI.**
