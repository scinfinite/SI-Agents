# Phase 27 — `si` CLI + Easy Setup

**Status: implementation complete; CI verification is required before merge.**

## Objective

Phase 27 adds the first user-facing control surface for SI-Agents. The `si` executable exposes environment diagnosis, status, canonical organization/workflow discovery, explicit setup, package update, and governed team execution without making the CLI a hidden policy or provider authority.

## Commands

```text
si doctor [--json]
si status
si agents
si teams
si setup [--apply] [--configure-opencode] [--opencode-url URL] [--omniroute-url URL]
si update [--apply]
si run TEAM --objective TEXT
```

### `doctor`

Delegates readiness checks to the existing Termux/Codespaces environment contracts. It preserves their exit codes: `0` ready, `2` degraded, `3` unsupported. JSON output is sanitized and does not expose credentials.

### `status`

Shows the detected environment, readiness state, workspace, configured OpenCode/OmniRoute endpoints, and the path of the non-secret SI configuration file.

### `agents` / `teams`

Load the canonical Phase 20 agent catalog and Phase 21 team catalog rather than maintaining a second CLI-specific inventory.

### `setup`

Default behavior is a dry-run plan. `--apply` is required before local mutation. Only commands supplied by the environment runtime's explicit setup/toolchain plan may execute; arbitrary shell strings are rejected. The CLI can also persist non-secret SI configuration and, with `--configure-opencode`, add/update an OmniRoute OpenAI-compatible provider in OpenCode's JSON configuration.

OpenCode credentials are not copied into SI configuration. The generated provider points at the configured OmniRoute endpoint and uses OpenCode's own credential/configuration mechanisms. JSONC configs are refused rather than parsed destructively.

### `update`

Default behavior is a dry-run package upgrade plan. `--apply` explicitly invokes the allowlisted Python package upgrade command. It does not silently pull Git branches or mutate a repository checkout.

### `run`

Executes an existing canonical team through `TeamEngine` and the existing agent worker implementations. The CLI does not grant permissions or bypass governance; team/worker/runtime policies remain authoritative. Catalog-only agents cannot be resolved as executable workers.

## Configuration

The CLI stores only non-secret configuration at `~/.config/si-agents/config.json` by default (or `SI_CONFIG`). Writes use an atomic replacement and restrictive `0700` directory / `0600` file permissions. Stored fields are environment, workspace, OpenCode URL, and OmniRoute URL.

No API key, password, provider credential, or OpenCode auth token is stored by Phase 27.

## OpenCode integration

Current OpenCode configuration supports an OpenAI-compatible provider with `providers.<id>.package = "@opencode/ai/providers/openai-compatible"` and a `settings.baseURL`. Phase 27 writes only the provider declaration; it does not install OpenCode, write OpenCode credentials, or guess model capabilities. Model discovery remains an OmniRoute responsibility.

## Security and governance boundaries

- Read-only commands do not execute arbitrary shell commands.
- Setup mutation requires explicit `--apply`.
- Setup execution is restricted to environment-provided, allowlisted command tuples.
- No secret persistence is introduced.
- OpenCode credentials remain under OpenCode's own auth/configuration boundary.
- OmniRoute remains the model/provider routing authority.
- The CLI does not create accounts, activate paid providers, or bypass Phase 13 governance.
- `run` uses the existing TeamEngine and agent/runtime authorization instead of creating a second permission system.

## Verification acceptance

Phase 27 is complete only when:

1. The built wheel exposes the `si` entry point.
2. The isolated wheel can import `core.cli` and invoke the parser.
3. CLI unit tests cover parser commands, non-secret config persistence, permission-restricted config storage, and canonical catalog discovery.
4. Ruff passes.
5. The complete pytest suite passes.
6. CI verifies build, isolated installation/import, lint, and tests.
7. Documentation and roadmap status match the verified implementation.

## Deliberate non-goals

Phase 27 does not implement cross-environment state synchronization, automatic Codespace creation, remote account provisioning, arbitrary shell execution, provider fallback logic, secret migration from OpenCode, or a new model router. Those remain outside the CLI boundary or belong to later phases.
