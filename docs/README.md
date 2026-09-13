# Documentation

## Current V4 baseline

SI-Agents V4 has completed Phases **44–69**. Phases **46, 47, 49, 50, 58, 59, and 60** are advanced-hardened. **Phase 69 — npm Distribution + Setup is implemented at 100%.**

The next roadmap phase is **Phase 70 — End-to-End Production Validation**. Phase 71 remains the final production-hardening gate.

See `architecture/SI_AGENTS_V4_PLAN.md` for the authoritative roadmap, `architecture/README.md` for the current architecture summary, `architecture/PHASES.md` for phase evidence, `architecture/phases/` for the canonical historical phase archive, and `../SIA_SPECS.md` for the complete system specification.

## Current hardening baseline

- **300 SI-native personas** are the current corpus target.
- Historical Phase records 1–68 are organized under `architecture/phases/`.
- `AGENTS.md` is the main repository-agent operating contract.
- `SIA_SPECS.md` is the complete current system specification.
- Low/Medium/High capacity policy is implemented in `core/capacity/`.
- Termux Low supports 1–2 selectable workers; Medium supports 3–5; High and heavy workloads are blocked locally.
- OpenCode and OmniRoute remain intentional SI-Agents integrations.
- Provenance, licensing, contributor, and external-branding controls are documented and audited.

## Phase 69 — npm Distribution + Setup

**100% implemented.** The npm surface is a thin launcher/bootstrapper over the authoritative Python SI runtime. It provides `npx si-agents`, global installation support, explicit `si-agents setup`, cross-platform Python discovery, an optional `SI_AGENTS_PYTHON` override, actionable prerequisite failures, package-content allowlisting, and automated npm/Python version and license checks.

The npm verifier runs `npm pack`, checks the exact published-file allowlist, and smoke-tests `--version` and `help`. CI runs the npm verifier together with the established Python build, wheel smoke, repository audit, integration verification, Ruff, compileall, and pytest gates.

Contract: `architecture/phases/PHASE_69_NPM_DISTRIBUTION_SETUP.md`.

## Phase 68 — Advanced CLI Platform

**100% complete and closed.** Phase 68 provides a transport-neutral CLI adapter over SI Core with governed run/task/execution operations, agent/team/workflow navigation, identity-bound approvals, bounded client sessions, events and bounded run streaming, model/provider discovery delegation, attachment inspection, non-secret config/auth status, transport profiles, and bounded declarative pipelines.

## Phase 67 — Advanced TUI Control Center

**100% complete and closed.** Phase 67 provides a dependency-free, keyboard-first terminal operator cockpit over the existing Control API with bounded selection, filtering, deterministic sorting, detail inspection, pause/live state, direct navigation, bounded JSON status export, non-interactive rendering, governed run creation, and identity-bound approval controls.

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
- Phase 69: npm distribution implementation and package verification are present on canonical `main`; final CI evidence is the release gate.

## V4 product surfaces

Web, TUI, CLI, npm, OpenCode, SDKs, workflows, and future runtimes remain clients/adapters of one authoritative SI Core. No interface creates competing execution/session/wait/workspace/evaluation/improvement authority.

## Next phase

**Phase 70 — End-to-End Production Validation**.

## Phase closure rule

A phase is not complete until implementation, unit/integration tests, adversarial/security tests, edge/failure tests, documentation synchronization, repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, SDK verification, and final exact-tree mainline CI are green. Phase 69 additionally requires npm package-content, version/license, and launcher smoke verification.
