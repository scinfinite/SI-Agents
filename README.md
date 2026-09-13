# SI-Agents

SI-Agents is a governed, evidence-driven AI engineering and agent platform built around one authoritative SI Core exposed through Web, TUI, CLI, SDKs, OpenCode, OmniRoute, workflows, and runtime/integration adapters.

## Phase 71 status

Phases **44–71 are closed**. Phase **71 — Final Production Hardening** is complete and verified on canonical `main`. The final hardening preserves SI Core as the sole execution authority while enforcing bounded lifecycle, idempotency, concurrency, and cancellation invariants at the RuntimeEngine boundary.

### npm distribution

```bash
npx si-agents --version
npx si-agents help
npx si-agents setup

npm install -g si-agents
si-agents setup
si-agents agents
```

The npm package requires Node.js 18+ and Python 3.11+ for runtime execution. It discovers `python3`/`python` on Unix-like systems and `python`/`py` on Windows, or uses `SI_AGENTS_PYTHON` when explicitly provided. It never becomes a competing execution or authorization authority: commands are forwarded to `core.cli.dispatch`.

`si-agents setup` is an explicit bootstrap operation that installs the matching Python package when it is not already importable. The npm tarball is deliberately allowlisted to the launcher, `LICENSE`, `NOTICE`, and `README.npm.md`; repository source, tests, CI files, and development artifacts are excluded.

## Phase 71 production hardening

The authoritative `RuntimeEngine` uses a bounded, thread-safe invocation ledger keyed by `(harness_id, request_id)`. Terminal responses are replayable, request-ID payload reuse fails closed, concurrent duplicates cannot execute a capability twice, cancellation is terminal, and lifecycle state is bounded. Full repository regression, packaging, npm, SDK, integration, audit, Ruff, and pytest gates were verified before and after merge.

See `docs/architecture/phases/PHASE_71_FINAL_PRODUCTION_HARDENING.md` for the final-hardening contract and acceptance record.

## Capacity profiles

```text
Low     Termux: 1–2 workers
Medium  Termux: 3–5 workers
High    Termux: blocked → Desktop/Codespace
```

Select through `SI_CAPACITY` and `SI_WORKERS`, or inspect the resolved policy with:

```bash
si-capacity --json
```

The capacity policy limits SI-controlled concurrency. It cannot guarantee a hardware temperature because OS, harness, provider, and hardware thermal behavior remain outside SI-Agents' complete authority.

## V4 roadmap

See `docs/architecture/SI_AGENTS_V4_PLAN.md` for the authoritative roadmap and `docs/architecture/PHASES.md` for phase evidence. Historical phase contracts live in `docs/architecture/phases/`.

| Phase | Name | Status |
|---:|---|---|
| 44 | Execution Runtime Foundation | Complete |
| 45 | Event Bus + State Architecture | Complete |
| 46 | Parallel Scheduler + Executor | Advanced hardened |
| 47 | OpenCode Bridge | Advanced hardened |
| 48 | OmniRoute Integration | Complete |
| 49 | Agent + Team Builder | Advanced hardened |
| 50 | Capability Authorization | Advanced hardened |
| 51 | Checkpoints + Resume | Complete |
| 52 | Context / Memory Economics | Complete |
| 53 | Persistent Sessions | Complete |
| 54 | Human-in-the-Loop | Complete |
| 55 | Durable Waiting + Scheduling | Complete |
| 56 | Intelligent Routing + Economics | Complete |
| 57 | Security Platform | Complete |
| 58 | Workspace / Worktree Lifecycle | Advanced hardened |
| 59 | Observability | Advanced hardened |
| 60 | Evaluation + Benchmarking | Advanced hardened |
| 61 | Continuous Improvement | Complete |
| 62 | Cross-Runtime / Cross-Harness | Complete |
| 63 | Ecosystem / Marketplace | Complete |
| 64 | SDK / Developer Platform | Complete |
| 65 | Workflow + Automation | Complete |
| 66 | Advanced Web Control Plane | Complete |
| 67 | Advanced TUI Control Center | Complete |
| 68 | Advanced CLI Platform | Complete |
| 69 | npm Distribution + Setup | **Complete / 100%** |
| 70 | End-to-End Production Validation | **Complete / 100%** |
| 71 | Final Production Hardening | **Complete / 100%** |

## Engineering gate

A phase is not complete until implementation, targeted tests, regression/integration tests, security/adversarial checks, packaging/distribution verification, repository/provenance audit, documentation synchronization, lint/syntax checks, and final exact-tree mainline CI are green.

## Core references

- `AGENTS.md` — agent operating rules.
- `SIA_SPECS.md` — complete system specification.
- `docs/architecture/PHASES.md` — current phase status.
- `docs/architecture/phases/README.md` — canonical phase archive.
- `docs/architecture/phases/PHASE_69_NPM_DISTRIBUTION_SETUP.md` — Phase 69 contract and acceptance record.
- `docs/architecture/phases/PHASE_70_END_TO_END_PRODUCTION_VALIDATION.md` — Phase 70 acceptance record.
- `docs/architecture/phases/PHASE_71_FINAL_PRODUCTION_HARDENING.md` — Phase 71 final hardening contract.
- `docs/architecture/CAPACITY_POLICY.md` — Low/Medium/High execution policy.
- `docs/platforms/TERMUX.md` — Termux operating contract.
- `docs/legal/PROVENANCE_AND_LICENSE.md` — provenance and legal-risk controls.
