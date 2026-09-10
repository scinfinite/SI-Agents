# SI-Agents Documentation

This directory is the maintained documentation surface for SI-Agents. Documentation is organized so operators can distinguish **current truth**, **historical implementation records**, **future roadmap**, and **governance/policy**.

## Start here

1. **Project overview:** `../README.md`
2. **Current phase/status:** `architecture/PHASES.md`
3. **Phase 29 canonical record:** `architecture/PHASE_29.md`
4. **Phase 30 canonical record:** `architecture/PHASE_30.md`
5. **Phase 31 canonical record:** `architecture/PHASE_31.md`
6. **v3 roadmap (next work):** `architecture/SI_AGENTS_V3.md`
7. **Architecture index:** `architecture/README.md`
8. **Engineering rules:** `../AGENTS.md`
9. **IP/provenance policy:** `../governance/legal/IP_PROVENANCE.md`

## Documentation map

```text
docs/
├── README.md
└── architecture/
    ├── README.md
    ├── PHASES.md
    ├── PHASE_29.md                            # Canonical Phase 29 record
    ├── PHASE_30.md                            # Canonical Phase 30 record
    ├── PHASE_31.md                            # Canonical Phase 31 record
    ├── SI_AGENTS_V3.md
    ├── PHASE_1_FOUNDATION.md
    ├── EXECUTION_BACKENDS.md
    └── PHASE_<n>_*.md                         # Historical phase contracts/evidence
```

The former `FOUNDATION.md` and duplicate `CONTROL_PLANE.md` names have been retired. Phase 1 is explicitly indexed as `PHASE_1_FOUNDATION.md`, and the important control-plane execution contract is consolidated into `PHASE_2_CONTROL_PLANE.md`.

## Source-of-truth rules

- `PHASES.md` is authoritative for current implementation status and verification.
- `PHASE_29.md` is the canonical Phase 29 architecture/parity/provenance/verification record.
- `PHASE_30.md` is the canonical portable Skill contract and verification record.
- `PHASE_31.md` is the canonical Rules/Hooks/Events contract and verification record.
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

As of the latest branch state, SI-Agents has completed **Phases 1–30** with mainline CI verification. Phase 31 implementation is complete and its final mainline CI run is the remaining closure gate.

**Next implementation after Phase 31 closure: Phase 32 — Memory & Knowledge.**
