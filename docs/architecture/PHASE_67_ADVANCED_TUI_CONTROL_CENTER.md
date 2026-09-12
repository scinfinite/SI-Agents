# Phase 67 — Advanced TUI Control Center

## Status

**Implementation complete / closure pending final CI.** Phase 66 was verified closed on `main` before Phase 67 began. Phase 67 is implemented on branch `phase-67-advanced-tui` and is designed as a dependency-free, keyboard-first client of the existing SI Control API.

## Contract

The TUI is an operator cockpit, not a second SI authority. It reads the same `ControlApiService` used by other control surfaces and routes all supported mutations through its governed methods. It does not execute shell commands, invoke providers, mutate workflows directly, bypass capability authorization, or own persistent execution state.

## Advanced surface

- 14 stable views remain compatible with the previous TUI contract.
- Operational overview, agents, teams, workflows, skills, memory, knowledge, evidence, runs, organization, governance, environments, harnesses, and settings remain available.
- Live refresh is explicit and bounded by the service read model; pause prevents refresh from replacing the current snapshot.
- Search/filtering is case-insensitive and local to the current read model.
- Sorting is deterministic and field-based for list views.
- Selection is bounded to the current result set.
- Detail mode expands the selected record without executing anything.
- Direct `view <name>` navigation and numbered views are supported.
- JSON export is bounded in the terminal status surface.
- Governed `run <action> <subject> [risk]` requests use `ControlApiService.create_run` and therefore remain subject to SI governance.
- Identity-bound `approve <id> <decision> <subject> <project> [reason]` uses `ControlApiService.decide_approval` and therefore remains inside the existing approval boundary.
- Non-interactive rendering supports CI and automation without terminal control sequences.
- `NO_COLOR` is respected.
- Page size is hard-bounded to 1–100.
- Unknown commands are inert and never become shell or HTTP execution.

## Safety invariants

1. **Single authority:** TUI owns presentation/navigation state only.
2. **No shell:** command input is parsed as TUI commands; it is never passed to a shell or subprocess.
3. **Governed mutation:** run and approval controls call existing Control API service boundaries.
4. **Bounded rendering:** list rows, terminal width, detail values, and exported status are bounded.
5. **Deterministic navigation:** selection and view transitions are bounded and reproducible.
6. **Graceful automation:** non-TTY mode renders once and exits successfully.
7. **Compatibility:** the historical 14-view names remain stable.

## Verification

Acceptance coverage: `tests/test_phase67_tui.py`, plus the existing `tests/test_phase41_tui.py` regression suite.

Required closure gate: implementation review, regression tests, advanced safety/adversarial tests, Ruff, compileall, full pytest, distribution/wheel verification, repository audit, integration verification, synchronized documentation, and final exact-tree mainline CI.

## Final closure

This document must only be changed to **Complete / 100%** after the final synchronized-tree mainline CI for the exact documentation state is green.
