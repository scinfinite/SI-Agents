# SI-Agents npm distribution

`si-agents` on npm is a small, cross-platform launcher for the SI-Agents Python runtime. It intentionally does **not** duplicate the runtime, authorization, agent catalog, or provider-routing logic.

## Requirements

- Node.js 18+
- Python 3.11+ for runtime execution

## Usage

Run the launcher with:

```text
npx si-agents --version
npx si-agents help
```

If the Python runtime is already installed and importable, normal commands are forwarded to the authoritative `core.cli.dispatch` entry point.

For a fresh machine, explicitly bootstrap the matching Python package:

```text
npx si-agents setup
```

Global installation is also supported:

```text
npm install -g si-agents
si-agents setup
si-agents agents
```

The `SI_AGENTS_PYTHON` environment variable may be used when Python is not the preferred executable on PATH.

## Termux and other Unix-like environments

Install Node.js and Python 3.11+ using the platform's supported package manager. The launcher does not assume `sudo`, systemd, or a desktop environment. Termux remains subject to SI-Agents capacity and heavy-workload policies enforced by the Python runtime.

## Windows

The launcher checks `python` and `py`, and otherwise reports a clear prerequisite error. It does not invoke a shell for runtime execution.

## Distribution safety

The npm package is deliberately allowlisted to the launcher, license/provenance files, and this npm-specific guide. Repository source, tests, CI files, development configuration, and local artifacts are not included in the npm tarball.

The npm version must match the Python package version. Publication is intentionally a separate release operation and requires the maintainer's npm account/registry credentials.
