# SI-Agents v3 — Product & Architecture Record

**Status:** v3 implementation complete and closed
**Baseline:** SI-Agents v2.0 + Phases 19–43 implemented and CI-verified
**Remaining:** none in the v3 implementation sequence
**Current successor:** SI-Agents v4 planning is recorded in `SI_AGENTS_V4_PLAN.md`
**Core principle:** one SI Core, one Control API, multiple operator/harness surfaces

## Architecture

SI-Agents v3 established the organization, intelligence, governance, verification, deployment planning, and control-plane layer around coding harnesses. It does not replace downstream harnesses or recreate provider routing authority.

```text
                    SI-AGENTS CORE
                          │
                    Control API v1
                          │
             ┌────────────┼────────────┐
             │            │            │
            CLI          TUI          Web
             │            │            │
             └────────────┼────────────┘
                          │
                   Runtime / Governance
                          │
                Harness / Environment
                          │
                       OmniRoute
```

Web and TUI are operator boundaries, not independent authorities. Deployment Center is a governed planning boundary. Final Integration Hardening is a verification boundary with no downstream execution authority.

## Phase 43 closure

**Complete + CI verified.** Phase 43 added the deterministic cross-cutting integration audit, packaged `si verify`/`si-verify`, canonical catalog/config consistency checks, deployment planning-only hardening, and adversarial release-gate coverage.

The final correction was merged as `52588921c0956f091fb569c4b51e9fd741790744`. Final mainline CI #886 (`34558002476`) passed the repository gates.

Canonical record: `PHASE_43_INTEGRATION_HARDENING.md`.

## v3 completion sequence

```text
29 Personas [complete]
 → 30 Skills [complete]
 → 31 Rules/Hooks/Events [complete]
 → 32 Memory/Knowledge [complete]
 → 33 Governance [complete]
 → 34 Organization [complete]
 → 35 Control API [complete]
 → 36 Web Foundation [complete]
 → 37 Control Center [complete]
 → 38 Visual Organization/Workflow [complete]
 → 39 Agent Builder [complete]
 → 40 Evidence/Observability [complete]
 → 41 TUI [complete]
 → 42 Harness Deployment [complete]
 → 43 Integration/Hardening [complete]
```

Each phase required implementation, tests, security/adversarial checks, documentation, relevant distribution verification, and successful CI. The v3 sequence is closed and must not be silently reopened.

## Transition to v4

v4 is an explicitly versioned successor, not unfinished v3 work. Its planning baseline is `SI_AGENTS_V4_PLAN.md` and covers Phases 44–55.

The primary architectural transition is from the completed v3 governance/control foundation to a real execution operating system with persistent runtime state, event/state synchronization, parallel scheduling, OpenCode and OmniRoute integration, a live Web control plane, improved TUI/CLI surfaces, workflow automation, and simple npm distribution.

The v4 implementation must preserve v3 authority boundaries, governance, evidence semantics, persona/Skill contracts, and provenance rules unless a versioned migration explicitly changes them.