# Phase 41 — SI TUI

## Purpose

Phase 41 adds a first-class terminal operator interface for Termux, Codespaces, SSH, and ordinary terminals. It is a dependency-free, keyboard-first view over the existing SI Control API service.

## Contract

- `core/tui/app.py` defines the immutable local `TuiState`, supported operator views, rendering, filtering, selection, navigation, and the interactive loop.
- `core/tui/cli.py` provides `si tui` and the packaged `si-tui` launcher.
- The TUI reads the same `ControlApiService` authority used by the Web surface.
- Views cover Overview, Agents, Teams, Workflows, Skills, Memory, Knowledge, Evidence, Runs, Organization, Governance, Environments, Harnesses, and Settings.
- `--once` provides deterministic non-interactive rendering for scripts and CI.
- `--filter` applies local, case-insensitive filtering to list views.
- `j/k` or `up/down` changes local selection; `n/p` changes views; `/text` sets a local filter; `r` refreshes; `q` exits.
- Terminal control sequences are emitted only for interactive TTY sessions; non-interactive execution renders once and exits.
- `NO_COLOR` and `--no-color` disable terminal control behavior.

## Authority and security boundary

The TUI has no mutation endpoints and no execution engine. It cannot create runs, authorize operations, grant capabilities, invoke Skills, execute workflows, invoke tools, run shell commands, control harnesses, or access credentials. Unknown commands are inert. Navigation and filtering mutate only the local `TuiState`.

There is one SI Core and one Control API. Web and TUI are operator surfaces, not competing authorities. The TUI deliberately consumes the same service methods as the Web Control Center instead of duplicating business logic.

## Packaging

- `si tui ...` is dispatched by `core.cli.dispatch`.
- `si-tui` is registered as a project script.
- `core.tui` is included by the existing package discovery rule.
- No third-party runtime dependency was added.

## Verification

Phase 40 was verified closed before Phase 41 started: main contained the Phase 40 documentation-closed commit `1a13c015eed3510987494c6f69941dc8b021a4e1`, and its final mainline CI **#864** (`34513486696`) was green with 458 tests passed.

Phase 41 implementation was merged from PR #43 as squash commit `531d2b964a6567aaa0a6b34b2d9b8f4471eb83f5`. Feature CI **#865** (`34553393908`) passed all repository gates, including build, wheel installation, repository audit, Ruff, tests, diagnostics, and cleanup. The post-merge implementation mainline CI **#866** (`34553461275`) also passed all gates.

Documentation closure is maintained separately so the final mainline gate can verify the complete documentation state. The phase is not considered closed until that final documentation commit has a green mainline CI run.

## Next phase

**Phase 42 — Harness Deployment Center.**
