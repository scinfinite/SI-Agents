# Phase 26 — GitHub Codespaces Runtime

## Status

**Complete and CI-verified.**

## Objective

Make SI-Agents inspectable and operationally ready inside GitHub Codespaces while preserving the existing governance, harness, and OmniRoute boundaries. Phase 26 adds environment detection and readiness validation; it is not an installer and does not grant execution authority.

## Contract

`core/environments/codespace.py` provides `CodespaceRuntime` and `CodespaceConfig`.

The runtime detects Codespaces using the `CODESPACES=true` marker or the Codespaces port-forwarding domain. It validates Python, Git, curl, OpenSSH, the Codespace workspace, and OpenCode by default. GitHub CLI, Node, and npm are optional unless explicitly required by configuration.

The runtime can optionally require OmniRoute health. When required, failure to configure or health-check OmniRoute degrades readiness rather than silently proceeding.

Reports reuse the vendor-neutral environment contracts from `core/environments/models.py`. JSON output contains readiness metadata only; API-key values are never emitted.

The runtime exposes a deterministic, read-only toolchain plan and workspace validation helper. Neither executes commands, installs packages, mutates OpenCode configuration, persists credentials, or bypasses Phase 13 governance.

## CLI

Human-readable:

```bash
python -m core.environments.codespace
```

Machine-readable:

```bash
python -m core.environments.codespace --json
```

Exit codes:

- `0` — ready
- `2` — degraded
- `3` — unsupported

## Boundaries

Phase 26 does not claim:

- automatic Codespace creation or lifecycle management;
- automatic package installation;
- automatic OpenCode installation or configuration;
- credential provisioning or persistence;
- model/provider routing outside OmniRoute;
- arbitrary shell-command execution;
- cross-environment state synchronization;
- the `si` CLI.

Those concerns remain in later phases or deployment infrastructure.

## Verification

The phase acceptance suite covers Codespaces detection, unsupported environments, missing OpenCode degradation, ready-state dependency checks, optional GitHub CLI requirements, non-executing toolchain planning, workspace validation, and secret-free reporting. CI must verify distribution build, isolated wheel installation/import, Ruff, and the complete pytest suite before completion is claimed.
