# Documentation

## Current V4 baseline

SI-Agents V4 has completed Phases **44–68**. Phases **46, 47, 49, 50, 58, 59, and 60** are advanced-hardened. **Phase 68 — Advanced CLI Platform is complete at 100%.**

Current hardening adds **300 agent personas across 18 divisions**, Low/Medium/High capacity controls, Termux guidance, repository-neutral provenance hygiene, Apache-2.0 licensing, and a systematic `docs/phases/` phase archive surface.

Use `SIA_SPECS.md` for the complete current system specification, `STATUS.md` for current status, `architecture/SI_AGENTS_V4_PLAN.md` for the roadmap, and `architecture/README.md` for the architecture summary.

## Phase 68 — Advanced CLI Platform

**100% complete and closed.** Phase 68 provides a transport-neutral CLI adapter over SI Core with governed run/task/execution operations, agent/team/workflow navigation, identity-bound approvals, bounded client sessions, events and bounded run streaming, model/provider discovery delegation, attachment inspection, non-secret config/auth status, transport profiles, and bounded declarative pipelines.

Local mode calls `ControlApiService`; remote mode uses authenticated HTTP. The CLI emits deterministic JSON envelopes and machine-readable failures, uses bounded request/response and local artifact sizes, never persists authentication secrets, never executes arbitrary shell commands, and fail-closes when downstream execution owns a lifecycle transition such as resume. Established legacy CLI commands remain backward compatible.

Closure evidence: PR #81 merged as `8c5fb08e9c8a5628f59cf929e3c2ac203d4eac29`; final PR CI #1319 / run `34703142494` and SDK CI #111 / run `34703142515` were green; final synchronized-tree mainline CI #1320 / run `34703212232` is green.

## Capacity and Termux

- Low: bounded inspection and short edits; allowed on Termux with one worker.
- Medium: bounded tests, lint, review, and analysis; allowed on Termux with two workers.
- High: compilation, large builds, benchmarks, large indexing, code generation, migrations; blocked locally on Termux and redirected to Desktop/Codespace.

The policy reduces SI-Agents-managed local load but cannot guarantee hardware temperature because external processes remain outside SI-Agents' direct control.

## Persona catalog

The runtime catalog is **300 personas / 18 divisions**. The base catalog plus repository-owned extension manifests are validated together by the persona parity gate.

## Legal/provenance controls

SI-Agents-owned work is licensed under Apache-2.0. Repository hygiene removes unnecessary external project branding from shipped surfaces. OpenCode and OmniRoute remain named because they are supported integrations. See `legal/PROVENANCE_AND_LICENSE.md`.

## Phase 67 — Advanced TUI Control Center

**100% complete and closed.** Phase 67 provides a dependency-free, keyboard-first terminal operator cockpit over the existing Control API. It preserves the historical 14-view surface while adding bounded selection, filtering, deterministic sorting, detail inspection, pause/live state, direct navigation, bounded JSON status export, non-interactive rendering, governed run creation, and identity-bound approval controls.

## Phase 66 — Advanced Web Control Plane

**100% complete and closed.** Phase 66 provides a secure, accessible, same-origin, dependency-free operational web client over the existing WebServer and versioned Control API.

## Phase 65 — Workflow + Automation

**100% complete.** Phase 65 provides a transport-neutral workflow state machine with versioned declarative DAGs, branching, bounded fan-out/loops, delegation, human gates, durable waits, triggers, retries, limits, cancellation, idempotency, checkpoints, templates, restart validation, and compensation.

## Closed-phase evidence

- Phase 61: merged PR #75 / PR CI #1157 (`34692165853`).
- Phase 62: merged PR #76; final mainline CI #1186 (`34693756693`) green.
- Phase 63: merged PR #77; final exact-tree mainline CI #1198 (`34694418960`) green.
- Phase 64: merged PR #78; closure CI #1239 (`34697885027`) passed.
- Phase 65: final synchronized-tree CI #1249 (`34698187600`) completed successfully.
- Phase 66: merged PR #79; final synchronized-tree mainline CI #1284 (`34701494501`) completed successfully.
- Phase 67: merged PR #80; final synchronized-tree mainline CI #1295 (`34702226193`) completed successfully.
- Phase 68: merged PR #81; final synchronized-tree mainline CI #1320 (`34703212232`) completed successfully.

## V4 product surfaces

Web, TUI, CLI, OpenCode, SDKs, workflows, and future runtimes remain clients/adapters of one authoritative SI Core. No interface creates competing execution/session/wait/workspace/evaluation/improvement authority.

## Next phase

**Phase 69 — npm Distribution + Setup.**

## Phase closure rule

A phase is not complete until implementation, tests, adversarial/security checks, documentation synchronization, repository audit, distribution verification, integration verification, lint/type/build checks, SDK verification, and final exact-tree mainline CI are green. **Phase 68 satisfies this closure rule.**
