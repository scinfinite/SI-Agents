# SI-Agents V4 Plan

## Authority

SI-Agents V4 is built around one authoritative SI Core. Web, TUI, CLI, OpenCode, runtime adapters, schedulers, agents, teams, workflows, SDKs, and integrations are clients/adapters, not competing state authorities.

```text
User → OpenCode / Web / TUI / CLI / SDK → SI Core / Control API
     → Scheduler / Orchestrator → Tasks / Agents / Teams / Workflows
     → Capability Authorization → OmniRoute → Models / Providers / APIs
     → Results / Artifacts / Evidence → SI Core
     → Observability → Evaluation → Continuous Improvement
     → Cross-Runtime → Ecosystem / Marketplace → Release Gates / Canaries / Rollback → Clients
```

OmniRoute owns model/provider/API routing. SI Core owns execution, orchestration, governance, evidence, lifecycle, persistence, recovery, waiting, workspaces, observability, evaluation, and improvement governance.

## Current position

V3 is closed. V4 has completed Phases **44–67**. Phases **46, 47, 49, 50, 58, 59, and 60** were advanced-hardened. **Phase 67 — Advanced TUI Control Center is closed at 100%. Phase 68 — Advanced CLI Platform is implementation-complete and is in its final CI/documentation closure gate.**

## Closed phases

Phases 44–67 are closed under their recorded implementation, merge, documentation, and CI evidence.

### Phase 67 — Advanced TUI Control Center

**Complete / 100%.** Phase 67 delivers a dependency-free, keyboard-first terminal operator cockpit over the existing Control API. It preserves the historical 14-view contract and adds bounded selection, filtering, deterministic sorting, detail inspection, pause/live state, direct navigation, bounded JSON status export, non-interactive rendering, governed run creation, and identity-bound approval controls.

`core/tui/app.py` owns only ephemeral presentation state. It never invokes a shell, creates a competing workflow/execution authority, or bypasses SI Core governance. All supported mutations go through `ControlApiService`. `core/tui/cli.py` provides strict root/view/filter/page-size/command controls, while `NO_COLOR` and non-interactive execution are supported for CI and automation.

Safety invariants include page-size bounds of 1–100, bounded terminal rendering, inert unknown commands, deterministic navigation, explicit pause state, no shell execution, and governed mutation routing.

Acceptance coverage: `tests/test_phase67_tui.py` plus `tests/test_phase41_tui.py`.

PR #80 merged successfully. Final PR CI **#1288** / run **34702115990** on commit `51eefc53a9d6a9073874d982a4e5c41be08269e2` completed successfully. The SDK workflow on the same tree also completed successfully as run **34702115987**.

### Phase 66 — Advanced Web Control Plane

**Complete / 100%.** Phase 66 provides a secure, accessible, same-origin operational web client over the existing WebServer and Control API. Final synchronized-tree mainline CI #1284 / `34701494501` is green.

### Phase 65 — Workflow + Automation

**Complete / 100%.** Phase 65 provides a transport-neutral declarative workflow engine with versioned DAGs, branching, bounded fan-out/loops, delegation, human gates, durable waits, triggers, retries, limits, cancellation, idempotency, checkpoints, templates, restart validation, and compensation. Final synchronized-tree CI #1249 / `34698187600` is green.

## Phase 68 — Advanced CLI Platform

**Implementation complete; final CI closure pending.** The Phase 68 platform is a transport-neutral command adapter over SI Core. It provides governed `run create/list/get`, task/execution inspection, agent/team/workflow resource navigation, identity-bound approval list/get/decide, bounded client sessions, event/state observation and bounded run streaming, model/provider discovery delegation, attachment inspection, non-secret config/auth status, and bounded declarative pipelines. Local mode calls `ControlApiService`; remote mode uses authenticated HTTP against the Control API.

The output contract supports deterministic JSON envelopes and exit classes for success, operational/validation failure, authentication failure, and governance/authority rejection. Safety bounds include 1 MiB remote request/response payloads, 10 MiB attachment inspection, 256 KiB pipeline files, 100 pipeline steps, 100 retained session records, bounded streaming, path-safe identifiers, and no arbitrary shell execution. Resume is explicitly fail-closed when the downstream execution engine owns the transition. Secrets are environment-only and never persisted by the CLI.

Implementation: `core/cli/platform.py`, `core/cli/aliases.py`, `core/cli/dispatch.py`.

Acceptance coverage: `tests/test_phase68_cli.py` plus the complete repository suite. Detailed contract: `docs/architecture/PHASE_68_ADVANCED_CLI_PLATFORM.md`.

## Phase 69 — npm Distribution + Setup

npm package/global CLI, one-command installation, platform/architecture detection, bootstrap/setup, OpenCode/OmniRoute detection/configuration, SI Core validation, diagnostics, upgrade/uninstall/migration, and clean-machine validation.

## Phase 70 — End-to-End Production Validation

Validate the complete OpenCode → SI → OmniRoute → provider/model → SI → OpenCode path across agents, teams, dependencies, reviews, fallback, limits, retries, cancellation, pause/resume, checkpoints, waits, approvals, restart/session/workspace recovery, security failures, context/cost limits, control surfaces, installation, upgrades, artifacts, evidence, telemetry, and evaluation.

## Phase 71 — Final Production Hardening

Final architecture, authority, state-machine, lifecycle, concurrency, idempotency, persistence, crash/restart, security, egress, tool/provider/runtime/context/scheduler/workspace/observability/UX/SDK/package/E2E audit with adversarial validation, performance/reliability, installation/upgrade, exact-tree, documentation, and final release evidence.

## Closure gate

A phase is closed only after implementation, unit/integration tests, adversarial/security tests, edge/failure tests, documentation synchronization, repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, and final exact-tree mainline CI are green. **Phase 68 is not declared closed until its merged documentation tree passes the final mainline CI gate.**