# SI-Agents Documentation

This directory is the maintained documentation surface for SI-Agents. Documentation distinguishes **current truth**, **historical implementation records**, **v4 planning**, and **governance/policy**.

## Start here

1. **Project overview:** `../README.md`
2. **Current phase/status:** `architecture/PHASES.md`
3. **Architecture index:** `architecture/README.md`
4. **v4 plan:** `architecture/SI_AGENTS_V4_PLAN.md`
5. **Completed v3 architecture:** `architecture/SI_AGENTS_V3.md`
6. **Phase 43 record:** `architecture/PHASE_43_INTEGRATION_HARDENING.md`
7. **CLI contract:** `architecture/CLI.md`
8. **Execution backends:** `architecture/EXECUTION_BACKENDS.md`
9. **Engineering rules:** `../AGENTS.md`
10. **IP/provenance policy:** `../governance/legal/IP_PROVENANCE.md`

The Phase 29–43 canonical records remain available from the architecture directory and preserve their phase-specific evidence.

## Source-of-truth rules

- `architecture/PHASES.md` is authoritative for current implementation status and verification.
- `architecture/README.md` is the maintained architecture navigation/index.
- `architecture/SI_AGENTS_V4_PLAN.md` is authoritative for the current v4 planning direction until implementation changes the contracts.
- Phase records are authoritative for their completed phase-time evidence.
- Runtime code, executable contracts, governance decisions, and CI results outrank prose when they conflict.
- Documentation must never claim a stronger implementation state than available evidence supports.

## Documentation lifecycle

When an implementation contract changes: implement and test; run the relevant verification; update the current status/index documentation; preserve historical evidence; and update the relevant phase record when the change belongs to an active phase.

## Security and provenance

Markdown is documentation/configuration, not an authority boundary. Imported or externally inspired content must not silently grant permissions or execute code. Material design influence must follow the project's provenance policy and be independently implemented.

## Current baseline

**Phases 1–43 are complete and CI-verified. v3 is closed.** The v4 planning baseline is now established in `architecture/SI_AGENTS_V4_PLAN.md`; Phase 44 has not started.

The final v3 mainline verification was CI #886 (`34558002476`), with distribution, wheel installation, repository audit, Ruff, and the complete pytest suite passing.

## Documentation status

The current-status/index Markdown files are maintained as living documents. Historical phase Markdown is intentionally not rewritten merely to reflect later v4 plans; those files preserve the evidence and contracts that were true when their phases were completed.