# Phase 25 — Termux Runtime

**Status: Complete — implementation and CI verified.**

## Objective

Make SI-Agents a first-class, inspectable runtime on Termux/Android without turning environment setup into an implicit security or credential boundary.

## Delivered

- Vendor-neutral environment readiness contracts and Termux detection.
- Python, Git, curl, OpenSSH, `pkg`, and OpenCode readiness checks.
- Optional fail-closed OmniRoute health requirement.
- Read-only doctor with sanitized human-readable/JSON output.
- Conservative package installation plan exposed as data rather than executed by the runtime.
- Read-only workspace validation.
- No credential emission or persistence.

## Runtime boundary

```text
Android → Termux → SI-Agents → OpenCode → OmniRoute → provider/model routing
```

SI-Agents remains the control/intelligence/governance layer. OpenCode remains the harness. OmniRoute remains the model/provider routing authority.

## Installation boundary

Termux package installation is an explicit setup concern. The runtime does not execute package-install commands itself. Later CLI setup consumes approved runtime plans through explicit mutation gates.

## Security and governance

The doctor does not print environment variable values, execute arbitrary commands, mutate OpenCode configuration, persist credentials, or bypass Phase 13 governance. Termux is an execution environment, not a complete security boundary.

## Verification coverage

Tests cover detection, unsupported environments, dependency readiness, OpenCode degradation, optional OmniRoute health, secret-free reports, package-plan generation, workspace validation, and doctor exit status. Distribution build, isolated wheel installation, Ruff, and full pytest verification completed for the phase.

## Current-state addendum

Phase 26 added Codespaces readiness; Phase 27 added the governed `si` setup/doctor surface; Phase 28 added portable handoff; Phase 29 added personas. The old Phase 25 non-goals describing those later phases are historical, not current gaps. Current status is Phase 29 complete and Phase 30 is next.
