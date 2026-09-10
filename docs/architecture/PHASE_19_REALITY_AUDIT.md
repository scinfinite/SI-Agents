# Phase 19 — v2.0 Reality Audit

**Status: Complete — evidence-backed audit and remediation committed.**

## Purpose

Phase 19 is the post-v2.0 reality check. Its purpose is to determine what Phases 1–18 actually deliver in executable form, identify gaps that would block the next SI-Agents direction, fix correctness issues that belong in the current baseline, and establish an evidence-backed boundary for future phases.

This phase deliberately does **not** implement OpenCode, OmniRoute, Termux, Codespaces, or the future agent-organization catalog. Those are evolution workstreams identified by the audit. Implementing them here would mix validation with the next architecture and make the phase completion claim less meaningful.

## Audit scope

The audit covered:

1. packaging and distribution;
2. CI/build/lint/test verification;
3. agent contracts and execution boundaries;
4. skills and reusable procedure boundaries;
5. runtime/harness interoperability;
6. governance enforcement at runtime boundaries;
7. evidence and verification boundaries;
8. existing end-to-end acceptance coverage;
9. project documentation/roadmap consistency;
10. readiness for future OpenCode/OmniRoute/environment integrations.

## Evidence inspected

### Repository and release state

- `README.md` declares v2.0 with Phases 1–18 complete.
- `docs/architecture/PHASES.md` declares Phases 1–18 complete and defines the completion rule.
- `AGENTS.md` is synchronized with the v2.0 state on the branch used for this phase.
- Main commit `f28f044bc0c5e5ce3b5e803e732c01f5b8cd7bba` had successful CI run #428.
- PR #1, which synchronizes `AGENTS.md`, passed CI run #429 before this phase branch was created.

### Runtime implementation

The runtime boundary contains:

- typed invocation request/response contracts;
- stable request correlation;
- project identity;
- optional project/harness sessions;
- declared runtime capabilities;
- normalized events and errors;
- explicit harness registration;
- deny-by-default harness execution;
- governance checks before adapter execution;
- response-shape validation;
- adapter conformance checks;
- a deterministic local reference adapter.

Existing runtime tests already cover governance denial, registration isolation, sessions, metadata normalization, conformance, cancellation, timeout behavior, malformed responses, adapter exception normalization, and unsupported capabilities.

Phase 19 adds a true integration-level runtime acceptance test that goes through a registered and enabled adapter, a project-scoped session, the `RuntimeEngine`, governance approval, streaming events, and a real capability handler.

### Agent implementation

The repository has a typed `AgentSpec`, `AgentContext`, `AgentResult`, and concrete Developer/Debugger/Tester agents. The current agent surface is intentionally small and is not yet a full organization/catalog comparable to Agency Agents.

This is an identified evolution gap, not a Phase 18 correctness failure.

### Skills implementation

The existing skills registry and validated skill catalog establish reusable, permission-aware procedures. Skills are not treated as policy authorities and selection does not itself grant execution permission.

The current skills layer is sufficient as a foundation for a future agent/team catalog; no Phase 19 redesign is required.

## Findings and dispositions

| Area | Finding | Disposition |
|---|---|---|
| Runtime contract | Strong typed transport-neutral boundary exists | Retain; add integration acceptance evidence |
| Governance | Runtime invocation requires governance and local adapter also enforces it | Retain defense-in-depth |
| Harness registration | Disabled-by-default registry exists | Retain; future adapters must use it |
| Runtime E2E | Unit coverage was strong, but a dedicated integration acceptance path was missing | **Fixed in Phase 19** |
| Packaging | `pyproject.toml` only discovered `core*` and `tools*`; the top-level `agents` package could be absent from built distributions | **Fixed in Phase 19** |
| Distribution verification | CI built artifacts but did not install/import the wheel in an isolated environment | **Fixed in Phase 19** |
| External harnesses | No OpenCode/Codex/Claude Code adapter is implemented yet | Future Phase 22+ work; intentionally not hidden as complete |
| Model gateway | No OmniRoute adapter/configurator is implemented yet | Future Phase 24 work |
| Termux runtime | No supported installer/runtime profile exists yet | Future Phase 25 work |
| Codespace runtime | Existing project CI/dev tooling is not yet a complete SI-Agents installer profile | Future Phase 26 work |
| CLI | No unified end-user `si setup`/`si doctor` surface exists yet | Future Phase 27 work |
| Agent organization | Typed agents exist, but there is no canonical division/team catalog | Future Phase 20–21 work |
| Cross-environment handoff | No portable task/session handoff contract is implemented | Future Phase 28 work |

## Correctness remediation

### 1. Package discovery

`pyproject.toml` now includes `agents*` alongside the existing `core*` and `tools*` package discovery patterns. The first distribution audit finding was therefore corrected instead of merely documented.

### 2. Wheel installation verification

CI now creates the project distributions and installs the produced wheel into a clean virtual environment. The isolated environment imports both `agents` and `core` and the runtime API before the normal lint/test stage.

This verifies that the build artifact, rather than only the source checkout, contains the packages required by the current architecture.

### 3. Runtime acceptance coverage

`tests/integration/test_runtime_e2e.py` exercises the governed runtime path end to end:

```text
registered adapter
  -> enabled harness
  -> project-scoped session
  -> RuntimeEngine
  -> governance decision
  -> capability handler
  -> streaming events
  -> completed response
```

The test also asserts that the real handler received the expected input and that the normalized event sequence is correct.

## Reality assessment

### What v2.0 can legitimately claim

SI-Agents v2.0 has a real, tested internal engineering platform with governance, tools, skills, evidence, memory, model/provider intelligence, automation, controlled learning, runtime interoperability contracts, and production-hardening controls. The local runtime path is executable and now has dedicated integration evidence.

### What v2.0 must not claim

v2.0 is **not yet** an end-user cross-harness agent platform. In particular, the following are not implemented merely because the runtime boundary exists:

- OpenCode integration;
- OmniRoute integration;
- Claude Code integration;
- Codex integration;
- Cline integration;
- Antigravity integration;
- Termux installation/runtime automation;
- GitHub Codespaces installation/runtime automation;
- unified `si setup`/`si doctor` CLI;
- canonical agent divisions and teams;
- portable cross-environment task handoff.

## Target architecture established by the audit

The next architecture should preserve the following separation:

```text
User
  -> Harness (OpenCode first)
  -> SI universal runtime boundary
  -> SI agents / teams / skills / workflows
  -> governed tools and verification

Model routing remains a separate concern:

OpenCode / future harness
  -> SI integration
  -> OmniRoute / compatible model gateway
  -> model providers

Environment remains a separate concern:

SI runtime
  -> Termux profile
  -> Codespace profile
  -> future environment profiles
```

This preserves vendor neutrality: OpenCode is a supported harness, not the SI core; OmniRoute is a model gateway, not the SI agent system; and Termux/Codespaces are environments, not agent definitions.

## Exit criteria

Phase 19 is complete when all of the following are true:

- [x] v2.0 implementation state inspected against source and tests.
- [x] runtime/harness boundary inspected.
- [x] governance enforcement inspected at the runtime boundary.
- [x] existing agent and skills boundaries inspected.
- [x] distribution configuration audited.
- [x] packaging gap corrected.
- [x] built-wheel installation verified by CI configuration.
- [x] dedicated runtime end-to-end acceptance coverage added.
- [x] current CI/build/lint/test verification path inspected.
- [x] documentation and roadmap boundaries recorded.
- [x] future integration gaps explicitly separated from current completion claims.
- [x] no future harness/environment integration is falsely declared complete.

## Verification evidence

The final completion claim is contingent on the Phase 19 branch CI run passing the repository's complete CI workflow, including:

1. distribution build;
2. isolated wheel installation/import;
3. Ruff;
4. full pytest suite, including the new runtime integration test.

If any of these checks fail, Phase 19 must remain incomplete until the failure is corrected and CI is rerun successfully.
