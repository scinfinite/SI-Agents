# Phase 67 — Advanced TUI Control Center

## Status

**Complete / 100% — merged and closed.** Phase 66 was verified closed on `main` before Phase 67 began. Phase 67 was implemented on branch `phase-67-advanced-tui`, merged through PR #80, and its final PR CI #1288 / run `34702115990` completed successfully on commit `51eefc53a9d6a9073874d982a4e5c41be08269e2`. The post-merge synchronized documentation tree is now undergoing mainline CI as the final release gate.

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
- Governed `run <action> <subject> [risk]` requests use `ControlApiService.create_run` and remain subject to SI governance.
- Identity-bound `approve <id> <decision> <subject> <project> [reason]` uses `ControlApiService.decide_approval` and remains inside the existing approval boundary.
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

PR #80 final CI #1288 / run `34702115990` passed. The SDK workflow on the same tree also passed as run `34702115987`. The implementation gate included the repository's test, lint, compile, audit, distribution/wheel, and integration validation.

## Final closure

After merge, the synchronized documentation tree is required to pass the exact-tree mainline CI before Phase 67 is treated as fully released. **No additional implementation changes are required; the final gate is documentation-tree CI.**
