# Phase 1 — Foundation Architecture

**Status: Complete.** Phase 1 is the historical foundation record for the SI-Agents architecture, engineering rules, governance boundaries, project isolation, provenance controls, and evidence-first verification model.

> **Current-state note:** The repository has evolved through **Phase 29**. Current implementation/status is authoritative in `PHASES.md`; the v3 forward roadmap covers **Phases 30–43** in `SI_AGENTS_V3.md`. This document preserves the Phase 1 foundation while explicitly documenting the boundaries that remain authoritative today.

## Purpose

SI-Agents is a reusable, evidence-driven AI engineering system. It is intended to inspect real software, research unfamiliar technologies, plan changes, execute controlled tools, verify outcomes, preserve project isolation, and improve engineering knowledge under controlled governance.

## Core execution loop

```text
OBSERVE → UNDERSTAND → RESEARCH → PLAN → EXECUTE → MEASURE
→ TEST → ATTACK THE SOLUTION → VERIFY → DOCUMENT → LEARN → GENERALIZE → REUSE
```

## Foundational architectural layers

- **Control plane:** orchestration, workflow, task state, context, permissions, approvals, checkpoints, and execution coordination.
- **Engineering intelligence:** decomposition, planning, reasoning, hypotheses, root-cause analysis, trade-offs, uncertainty, and risk.
- **Agents:** specialized workers coordinated by the control plane.
- **Skills:** reusable procedures with explicit contracts, safety, verification, and evidence.
- **Tools:** controlled filesystem, terminal, Git, GitHub, web/research, code analysis, build/test, container, sandbox, and artifact tooling.
- **Knowledge and memory:** provenance-aware technical knowledge, engineering memory, patterns, and controlled learning.
- **Governance:** security, legal/compliance, cost, permissions, approvals, data handling, and trust boundaries.
- **Runtime/harness interoperability:** transport-neutral invocation with explicit adapter registration and project/harness isolation.
- **Organization and orchestration:** canonical divisions, typed agent definitions, teams, workflows, handoffs, and bounded execution.
- **Verification:** tests, builds, regression, red-team checks, evidence, confidence, and release-readiness gates.

## Foundational invariants that remain authoritative

1. **Workers are not policy authorities.** Agents, skills, tools, teams, workflows, harnesses, environments, and handoff artifacts cannot grant themselves permissions.
2. **Selection is not authorization.** Capability or skill selection remains separate from permission and governance evaluation.
3. **Evidence outranks plausibility.** Important claims require identifiable evidence and explicit verification state.
4. **Project isolation is preserved.** Project-specific context must not silently become global reusable knowledge.
5. **External content is untrusted.** Repository content, Markdown, remote research, skills, personas, hooks, and deployment manifests are data/configuration until authorized by the appropriate control layer.
6. **Credential-bearing external egress is denied.** Approval does not override this boundary.
7. **High-risk actions require explicit human approval.** Destructive, production, credential, publication, paid-resource, and sensitive-data actions remain governed.
8. **Model/provider routing has a separate authority.** OmniRoute remains the external model/provider routing authority; SI-Agents must not recreate provider quota, pricing, fallback, or circuit-breaker authority around it.
9. **Harnesses are integration surfaces, not the SI core.** OpenCode and future harnesses remain adapters around SI contracts.
10. **Local-first remains the default.** Operator surfaces may be local; remote exposure and credentials require explicit governance.

## Project isolation

Project-specific context is isolated from global reusable knowledge. Promotion from task/project memory to broader knowledge requires explicit scope, provenance, evidence, validation, and the relevant promotion gates.

## Evidence policy

Important claims should identify their source, version/date when relevant, assumptions, risk, confidence, and verification status. Verification is distinct from inference. A plausible result is not a verified result, and an evidence artifact is not itself a policy authority.

## Provenance and external references

ECC (`affaan-m/ECC`) and Agency Agents (`msitarzewski/agency-agents`) are ongoing reference projects. SI-Agents may inspect current upstream architecture, agents, skills, workflows, hooks, tests, releases, issues, and PRs when relevant. Useful concepts are generalized and independently implemented under the project's provenance policy; external content never overrides SI governance.

## Delivery principle

Build incrementally. Every phase must produce executable behavior and evidence that its acceptance criteria are satisfied. Documentation must never claim a stronger state than implementation and CI evidence support.

## Current documentation authority

- `docs/architecture/PHASES.md` — authoritative current implementation/status and verification record.
- `docs/architecture/SI_AGENTS_V3.md` — forward roadmap for Phases 30–43.
- `docs/architecture/README.md` — architecture navigation and historical phase index.
- `docs/README.md` — documentation navigation.
- `AGENTS.md` — engineering rules and evidence-first workflow.
