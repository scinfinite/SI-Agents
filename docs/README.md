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
├── README.md                         # This index
└── architecture/
    ├── README.md                     # Architecture navigation
    ├── PHASES.md                     # Authoritative status + verification history
    ├── SI_AGENTS_V3.md               # Forward roadmap: Phases 29–43
    ├── FOUNDATION.md                 # Foundational architecture
    ├── CONTROL_PLANE.md              # Control-plane architecture
    ├── EXECUTION_BACKENDS.md         # Execution backend boundary
    └── PHASE_<n>_*.md                 # Historical phase contracts/evidence
```

## Source-of-truth rules

- `PHASES.md` is authoritative for what is implemented and verified.
- `SI_AGENTS_V3.md` is authoritative for forward-looking v3 planning.
- Individual `PHASE_<n>_*.md` files are historical implementation records; they must not be edited to claim capabilities that were added later.
- Runtime, governance, and code contracts remain authoritative over prose.
- README/documentation status must never outrun implementation or CI evidence.

## Documentation lifecycle

When a phase changes state:

1. Implement and test the code.
2. Run the required CI gates.
3. Record the verified result in `PHASES.md`.
4. Update the relevant detailed phase document if its completion evidence or boundaries changed.
5. Update root README and indexes when the public project state changes.
6. Keep future roadmap text clearly separated from completed functionality.

## Security and provenance

Markdown is documentation/configuration, not an authority boundary. Imported or externally inspired content must not silently grant permissions or execute code. Material external design influence must follow the project's provenance policy and be independently implemented.

## Current baseline

As of the latest verified mainline state, SI-Agents has completed **Phases 1–28**. Phase 28's mainline CI verification is run **#526** on commit `4ccfcfe29693d2a0f76810c000607822938253f4`, with **341 tests passing**. The next planned implementation is Phase 29.
