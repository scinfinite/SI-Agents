# SI-Agents

SI-Agents is a governed, evidence-driven AI engineering and agent platform built around one authoritative SI Core exposed through Web, TUI, CLI, SDKs, OpenCode, OmniRoute, workflows, and runtime/integration adapters.

## Pre-Phase 69 hardening status

Phases **44–68 are closed**. Before Phase 69 begins, the repository has a dedicated hardening gate covering documentation organization, the 300-persona target, provenance/license hygiene, Termux capacity controls, and runtime verification.

### Current hardening baseline

- **300 SI-native persona definitions** are the target/current corpus, with 21 independently authored repository extensions merged through the catalog loader.
- Historical phase records **1–68** are now canonically stored under `docs/architecture/phases/`.
- `AGENTS.md` is the main repository-agent operating contract.
- `SIA_SPECS.md` is the complete current system specification.
- `core/capacity/` provides Low/Medium/High capacity governance.
- Termux Low supports **1–2 selectable workers**.
- Termux Medium supports **3–5 selectable workers**.
- Termux High and heavy build/compile workloads are blocked and redirected to Desktop/Codespace.
- OpenCode and OmniRoute remain supported SI-Agents integration boundaries.
- Repository provenance/branding checks reject unnecessary external inspiration-project names from operational surfaces.
- Apache-2.0 licensing/notice and contributor provenance policies are documented.

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
| 69 | npm Distribution + Setup | **Next — blocked until hardening gate closes** |

## Engineering gate

A phase is not complete until implementation, targeted tests, regression/integration tests, security/adversarial checks, packaging/distribution verification, repository/provenance audit, documentation synchronization, lint/syntax checks, and final exact-tree mainline CI are green.

## Core references

- `AGENTS.md` — agent operating rules.
- `SIA_SPECS.md` — complete system specification.
- `docs/architecture/PHASES.md` — current phase status.
- `docs/architecture/phases/README.md` — canonical phase archive.
- `docs/architecture/CAPACITY_POLICY.md` — Low/Medium/High execution policy.
- `docs/platforms/TERMUX.md` — Termux operating contract.
- `docs/legal/PROVENANCE_AND_LICENSE.md` — provenance and legal-risk controls.

**Phase 69 must not start until this hardening branch passes its complete CI and exact-tree verification gate.**
