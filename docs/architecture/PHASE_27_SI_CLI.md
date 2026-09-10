# Phase 27 — `si` CLI + Easy Setup

**Status: complete and CI-verified.**

## Objective

Phase 27 adds the first user-facing control surface for SI-Agents. The `si` executable exposes environment diagnosis, status, canonical organization/workflow discovery, explicit setup, package update, and governed team execution without making the CLI a hidden policy or provider authority.

## Commands

```text
si doctor [--json]
si status
si agents
si teams
si setup [--apply] [--configure-opencode] [--opencode-url URL] [--omniroute-url URL] [--model MODEL]
si update [--apply]
si run TEAM --objective TEXT
```

### `doctor`

Delegates readiness checks to the existing Termux/Codespaces environment contracts. It preserves their exit codes: `0` ready, `2` degraded, `3` unsupported. JSON output is sanitized and does not expose credentials.

### `status`

Shows the detected environment, readiness state, workspace, configured OpenCode/OmniRoute endpoints, selected non-secret model ID, and the path of the non-secret SI configuration file.

### `agents` / `teams`

Load the canonical Phase 20 agent catalog and Phase 21 team catalog rather than maintaining a second CLI-specific inventory. Both catalogs are packaged into the distribution, so an installed wheel does not require a source checkout.

### `setup`

Default behavior is a dry-run plan. `--apply` is required before local mutation. Only commands supplied by the environment runtime's explicit setup/toolchain plan may execute; arbitrary shell strings are rejected. The CLI can also persist non-secret SI configuration and, with `--configure-opencode --model MODEL`, add/update an OmniRoute OpenAI-compatible provider in OpenCode's JSON configuration.

OpenCode credentials are not copied into SI configuration. The generated provider points at the configured OmniRoute endpoint and uses OpenCode's own credential/configuration mechanisms. JSONC configs are refused rather than parsed destructively. The model must be explicit because OmniRoute's `/v1/models` surface can contain multiple model modalities and SI-Agents does not guess chat capability.

### `update`

Default behavior is a dry-run package upgrade plan. `--apply` explicitly invokes the Python package upgrade command. It does not silently pull Git branches or mutate a repository checkout.

### `run`

Executes an existing canonical team through `TeamEngine` and the existing agent worker implementations. The CLI does not grant permissions or bypass governance; team/worker/runtime policies remain authoritative. Catalog-only agents cannot be resolved as executable workers.

## Configuration

The CLI stores only non-secret configuration at `~/.config/si-agents/config.json` by default (or `SI_CONFIG`). Writes use an atomic replacement and restrictive `0700` directory / `0600` file permissions. Stored fields are environment, workspace, OpenCode URL, OmniRoute URL, and an optional model ID.

No API key, password, provider credential, or OpenCode auth token is stored by Phase 27.

## OpenCode integration

Current OpenCode configuration supports an OpenAI-compatible provider with `providers.<id>.package = "@opencode/ai/providers/openai-compatible"` and a `settings.baseURL`. Phase 27 writes only the provider declaration and an explicitly selected model; it does not install OpenCode, write OpenCode credentials, or guess model capabilities.

## Security and governance boundaries

- Read-only commands do not execute arbitrary shell commands.
- Setup mutation requires explicit `--apply`.
- Setup execution is restricted to environment-provided, allowlisted command tuples.
- No secret persistence is introduced.
- OpenCode credentials remain under OpenCode's own auth/configuration boundary.
- OmniRoute remains the model/provider routing authority.
- The CLI does not create accounts, activate paid providers, or bypass Phase 13 governance.
- `run` uses the existing TeamEngine and agent/runtime authorization instead of creating a second permission system.

## Verification evidence

Phase 27 acceptance was verified by PR #14 CI run **#499**:

1. The built wheel exposed the `si` console entry point.
2. The isolated wheel imported the core packages and executed `si agents` and `si teams`, proving canonical catalogs are available after installation.
3. CLI unit tests covered all commands, non-secret configuration persistence, restrictive configuration permissions, and canonical catalog discovery.
4. Ruff passed.
5. The complete pytest suite passed with **330 tests**.

Two earlier failures were corrected rather than suppressed: CI #495 exposed an invalid exception type under Ruff; CI #497 exposed an incomplete CLI parser test. The corrected CI #499 run passed all build, wheel, lint, and test gates.

The PR was merged as commit **7308549553e9cc15f3d393b283974a26c9425a73**. README and the phase roadmap were synchronized to the verified state after merge.

## Deliberate non-goals

Phase 27 does not implement cross-environment state synchronization, automatic Codespace creation, remote account provisioning, arbitrary shell execution, provider fallback logic, secret migration from OpenCode, or a new model router. Those remain outside the CLI boundary or belong to later phases.
