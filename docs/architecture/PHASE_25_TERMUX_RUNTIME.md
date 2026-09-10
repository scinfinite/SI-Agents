# Phase 25 — Termux Runtime

## Objective

Make SI-Agents a first-class, inspectable runtime on Termux/Android without turning environment setup into an implicit security or credential boundary.

## Delivered

- `core.environments` introduces vendor-neutral environment readiness contracts.
- `TermuxRuntime` detects Termux using `TERMUX_VERSION` and the Termux `PREFIX` layout.
- Readiness checks cover Python, Git, curl, OpenSSH, the Termux `pkg` manager, and OpenCode.
- Readiness can optionally require a healthy OmniRoute gateway using the Phase 24 client.
- The doctor is read-only: it does not install packages, mutate OpenCode configuration, write credentials, or modify a workspace.
- `python -m core.environments.termux` provides a direct Termux doctor with human-readable or `--json` output and non-zero exit codes for degraded/unsupported environments.
- A conservative `pkg` installation plan is exposed as data for later setup automation; this phase does not execute it.
- Workspace validation checks existence, directory type, and readability without creating or deleting files.
- Environment reports are sanitized and JSON-compatible; API keys are never emitted.

## Termux architecture boundary

```text
Android
  |
  v
Termux
  |
  +--> Python / SI-Agents
  |
  +--> OpenCode harness
  |
  +--> OmniRoute gateway
  |       |
  |       +--> provider/model routing
  |
  +--> Git / SSH / repository workspace
```

SI-Agents remains the control/intelligence/governance layer. OpenCode remains the harness. OmniRoute remains the model/provider routing authority established by Phase 24.

## Runtime readiness policy

The default required commands are `git`, `python`, `curl`, `ssh`, and `pkg`. OpenCode is required by default because the target user workflow uses OpenCode as the harness. Node/npm are observed as optional capabilities rather than hard requirements because OpenCode may be installed through its standalone installer rather than a package-manager workflow.

A deployment can require OmniRoute explicitly by supplying an `OmniRouteConfig`. When required, the doctor fails closed unless the gateway health check succeeds. The API key is read only from the existing environment-variable boundary; it is never printed or persisted.

The runtime accepts loopback HTTP for local OmniRoute, consistent with Phase 24. Remote OmniRoute endpoints retain Phase 24's HTTPS requirement.

## Installation boundary

Termux package installation remains an operator/setup concern in this phase. The runtime exposes the conservative package plan:

```text
pkg update
pkg install -y git python curl openssh
```

No automatic package installation is performed by the Python runtime. This prevents a library import or health check from unexpectedly mutating an Android environment. The later `si` setup phase may consume this plan through an explicit, reviewable setup workflow.

[OpenCode's official installation documentation](https://opencode.ai/docs) provides the current install script and package-manager alternatives. Phase 25 does not hard-code a particular OpenCode binary version; the doctor only validates that an `opencode` executable is available. This avoids coupling the runtime to a fast-moving harness release.

[OmniRoute's CLI integration documentation](https://github.com/diegosouzapw/OmniRoute/blob/release/v3.8.51/docs/reference/CLI-TOOLS.md) documents the OpenAI-compatible local gateway and `setup-*` helpers for clients such as OpenCode. Phase 25 deliberately does not invoke those helpers or mutate OpenCode configuration; that belongs to explicit setup/configuration work.

## Security and governance

- No credentials are written to the repository, Termux dotfiles, or OpenCode config.
- The doctor does not print environment variable values.
- API keys are represented only as a boolean configured/not-configured signal.
- The runtime does not execute package-install commands itself.
- The runtime does not provide an arbitrary command executor, preventing environment checks from becoming a governance bypass.
- Workspace validation is read-only.
- OmniRoute provider credentials, fallback, quota, pricing, and routing remain outside SI-Agents authority.
- Termux is an execution environment, not a security boundary; Android/Termux permissions and operator controls remain deployment responsibilities.

## Verification coverage

Tests cover:

- Termux detection and non-Termux fail-closed behavior;
- complete readiness when required commands are present;
- missing OpenCode degradation;
- required healthy OmniRoute behavior;
- secret-free JSON report serialization;
- non-executing package-plan generation;
- read-only workspace validation;
- doctor CLI output and exit status.

CI must verify distribution build, isolated wheel installation/import, Ruff, and the complete pytest suite before Phase 25 is declared complete.

## Explicit non-goals

Phase 25 does not implement:

- the `si` setup/doctor CLI;
- automatic package installation;
- automatic OpenCode installation or version pinning;
- OpenCode configuration mutation;
- persistent OmniRoute credentials;
- OmniRoute provider administration;
- Codespace runtime support;
- cross-environment session handoff;
- persistent environment state synchronization;
- automatic paid-provider activation.

These remain Phase 26–29 concerns or deployment/operator responsibilities.
