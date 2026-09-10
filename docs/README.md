# SI-Agents Documentation

This directory is the maintained documentation surface for SI-Agents. Documentation is organized so operators can quickly distinguish **current truth**, **historical implementation records**, **future roadmap**, and **governance/policy**.

## Start here

1. **Project overview:** `../README.md`
2. **Current phase/status:** `architecture/PHASES.md`
3. **v3 roadmap (next work):** `architecture/SI_AGENTS_V3.md`
4. **Architecture index:** `architecture/README.md`
5. **Engineering rules:** `../AGENTS.md`
6. **IP/provenance policy:** `../governance/legal/IP_PROVENANCE.md`

## Documentation map

```text
docs/
├── README.md                                  # This index
└── architecture/
    ├── README.md                              # Architecture navigation + historical index
    ├── PHASES.md                              # Authoritative current status + verification history
    ├── SI_AGENTS_V3.md                        # Forward roadmap: Phases 30–43
    ├── PHASE_1_FOUNDATION.md                  # Historical Phase 1 foundation
    ├── EXECUTION_BACKENDS.md                  # Cross-cutting execution backend boundary
    └── PHASE_<n>_*.md                         # Historical phase contracts/evidence
```

The former `FOUNDATION.md` and duplicate `CONTROL_PLANE.md` names have been retired. Phase 1 is now explicitly indexed as `PHASE_1_FOUNDATION.md`, and the important control-plane execution contract is consolidated into `PHASE_2_CONTROL_PLANE.md`.

## Source-of-truth rules

- `PHASES.md` is authoritative for what is implemented and verified.
- `SI_AGENTS_V3.md` is authoritative for forward-looking v3 planning.
- `PHASE_1_FOUNDATION.md` and individual `PHASE_<n>_*.md` files are historical implementation records; they preserve phase-time scope while carrying only concise current-state boundary notes where needed.
- Runtime, governance, executable contracts, and CI results remain authoritative over prose.
- README/documentation status must never outrun implementation or CI evidence.

## Documentation lifecycle

When a phase changes state:

1. Implement and test the code.
2. Run the required CI gates.
3. Record the verified result in `PHASES.md`.
4. Update the relevant detailed phase document if its completion evidence or boundaries changed.
5. Update root README and indexes when the public project state changes.
6. Keep future roadmap text clearly separated from completed functionality.
7. Preserve historical phase evidence instead of rewriting it to claim that the phase originally contained later features.

## Security and provenance

Markdown is documentation/configuration, not an authority boundary. Imported or externally inspired content must not silently grant permissions or execute code. Material external design influence must follow the project's provenance policy and be independently implemented.

## Current baseline

As of the latest verified mainline state, SI-Agents has completed **Phases 1–29**. Phase 29 is CI-verified with the final mainline suite at **352 tests passed**; the authoritative verification details are recorded in `docs/architecture/PHASES.md`.

**Next implementation: Phase 30 — First-Class Portable Skills.**
