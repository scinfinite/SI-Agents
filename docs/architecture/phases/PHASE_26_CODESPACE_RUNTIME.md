# Phase 26 — GitHub Codespaces Runtime

**Status: Complete and CI-verified.**

## Objective

Make SI-Agents inspectable and operationally ready inside GitHub Codespaces while preserving the existing governance, harness, and OmniRoute boundaries. Phase 26 adds environment detection and readiness validation; it is not an installer and does not grant execution authority.

## Contract

`core/environments/codespace.py` provides `CodespaceRuntime` and `CodespaceConfig`. The runtime detects Codespaces, validates Python/Git/curl/OpenSSH/workspace/OpenCode by default, and can optionally require OmniRoute health. GitHub CLI, Node, and npm are optional unless explicitly required.

Reports contain readiness metadata only; API-key values are never emitted. Toolchain planning and workspace validation are read-only and do not execute commands, install packages, mutate OpenCode configuration, persist credentials, or bypass governance.

## CLI

```bash
python -m core.environments.codespace
python -m core.environments.codespace --json
```

Exit codes: `0` ready, `2` degraded, `3` unsupported.

## Boundaries

Phase 26 does not itself create Codespaces, install packages, provision credentials, execute arbitrary shell commands, synchronize cross-environment state, or implement the `si` CLI. Those were deliberately delegated to later layers.

## Verification

The phase acceptance suite covers Codespaces detection, unsupported environments, missing OpenCode degradation, ready-state dependency checks, optional GitHub CLI requirements, non-executing toolchain planning, workspace validation, and secret-free reporting. Distribution build, isolated wheel installation, Ruff, and the complete pytest suite are part of the completion gate.

## Current-state addendum

Later Phase 27 introduced the governed `si` CLI/setup layer and Phase 28 introduced explicit portable handoff. Phase 29 introduced agent personas. Those later capabilities surround, rather than replace, the Codespaces readiness contract. Current status is Phase 29 complete; Phase 30 is next.
