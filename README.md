# SI-Agents

SI-Agents is an evidence-driven AI engineering system designed to inspect software, diagnose problems, execute controlled changes, verify results, and learn reusable engineering patterns.

## Current status

**Post-v2 evolution — Phase 20 complete and CI-verified.**

Completed foundation through Production Hardening and the first post-v2 organization layer:

- **Phase 1 — Foundation:** architecture, engineering rules, governance, project isolation, security/cost/learning/compliance policies, provenance controls, and verification standards.
- **Phase 2 — Control Plane:** task lifecycle, persistence, dependencies, retries, context isolation, agents, workflows, permissions, approvals, checkpoints, execution state, and evidence integration.
- **Phase 3 — Tool System:** controlled filesystem, terminal, Git, GitHub, web, code analysis, build/test, container, sandbox, and artifact tooling with registry and permission enforcement.
- **Phase 4 — Engineering Brain:** problem normalization, decomposition, dependency-aware planning, reasoning, hypotheses, root-cause analysis, trade-offs, uncertainty, risk, and capability-aware planning.
- **Phase 5 — Developer/Debugger/Tester:** explicit agent contracts and the inspect → reproduce → diagnose → checkpoint → repair → test → red-team → regression → verify → document workflow.
- **Phase 6 — Skills Engine:** reusable skill contracts, lifecycle states, validated selection, permissioned execution, explicit verification, evidence recording, and an initial engineering skill catalog.
- **Phase 7 — Verification + Evidence:** bounded claims, provenance-aware evidence, confidence assessment, fail-closed verification, regression suites, red-team falsification, before/after benchmarks, and production-readiness gates.
- **Phase 8 — Technical Knowledge:** universal language schema, provenance-aware knowledge contracts, runtime catalog loading, multi-language coverage including Java, framework/ecosystem catalog, and engineering standards catalog.
- **Phase 9 — Technology Discovery:** repository technology/build detection, explicit uncertainty, safe experimentation contracts, declaration-based compatibility checks, and provenance-preserving knowledge proposals.
- **Phase 10 — Open-Source Intelligence:** repository metadata, archaeology/history, issues, pull requests, releases, security advisories, conservative license assessment, project health, freshness, and a read-only provider contract.
- **Phase 11 — Pattern Extraction:** deterministic observation normalization, conservative candidate extraction, independent evidence validation, counterexample handling, evidence-gated promotion, versioning, provenance, and context matching.
- **Phase 12 — Engineering Memory:** task/project/global scopes, provenance and verified evidence, fail-closed one-step promotion, deterministic scoped retrieval, expiration, supersession/versioning, and auditable JSON persistence.
- **Phase 13 — Security + Legal + Cost:** executable governance decisions, conservative risk classification, data-egress controls, provenance/legal review, free-first paid-resource controls, explicit approvals, and audit evidence.
- **Phase 14 — Model/Provider Intelligence:** typed model/provider capabilities, explicit registration, quota observations, deterministic capability/cost/latency routing, reliability/health tracking, fallback constraints, and provider circuit breakers.
- **Phase 15 — Automation:** one-shot/recurring schedules, deterministic due selection, lifecycle controls, registered actions, conditional triggers, bounded retries/backoff, idempotency, governance-gated execution, run history, and dependency-free JSON persistence.
- **Phase 16 — Controlled Self-Improvement + Capability Intelligence:** evidence-backed improvement proposals, benchmark/regression/safety gates, explicit approval, rollback, deterministic capability readiness scoring, conservative unknown handling, and auditable JSON persistence.
- **Phase 17 — Harness & Runtime Interoperability:** transport-neutral invocation envelopes, runtime capability negotiation, normalized events/errors, project-scoped sessions, explicit harness registry, governed local adapter, and adapter conformance testing.
- **Phase 18 — Production Hardening:** deterministic readiness checks, explicit resource limits, conservative telemetry redaction, evidence-based release gates, production policy, migration/rollback requirements, and hardened CI execution.
- **Phase 19 — v2.0 Reality Audit:** executable baseline audit, distribution correctness, isolated wheel verification, runtime E2E acceptance, and explicit future-boundary definition.
- **Phase 20 — Agent Organization & Catalog:** canonical divisions and agent definitions, typed catalog registry, declarative capability/permission/environment/harness selection, lifecycle status, implementation references, and validation tests.

## Engineering loop

```text
OBSERVE → UNDERSTAND → RESEARCH → PLAN → EXECUTE → MEASURE
→ TEST → ATTACK THE SOLUTION → VERIFY → DOCUMENT → LEARN → GENERALIZE → REUSE
```

## Control and safety model

Agents, capabilities, tools, skills, knowledge, and automation jobs are workers/data—not policy authorities. Registration or selection does not grant permission. High-risk actions remain approval-gated, repository mutation remains protected, and important claims require evidence.

Automation is a scheduling and execution mechanism, not a second policy engine. The scheduler selects due jobs but never executes them; the runner only invokes explicitly registered actions and evaluates the existing governance boundary first. Paid resources, sensitive/confidential egress, destructive operations, and publication remain subject to Phase 13 controls. Retries are bounded, idempotency is explicit, and cancelled jobs cannot silently resume.

Controlled learning is also not a policy authority. It can propose and evaluate improvements, but it cannot silently mutate code or promote capabilities. Benchmark, regression, and safety gates must pass before approval; application and rollback are explicit externally supplied operations. Capability intelligence is advisory and conservative when evidence is missing.

Runtime interoperability is also not a policy authority. Harness adapters translate transport concerns only; explicit registration is disabled by default, project identity is mandatory, unsupported capabilities fail closed, and invocations require the existing governance boundary. The local reference adapter is not a host security boundary.

The organization catalog is also not an execution authority. Catalog membership describes an agent; selection narrows candidates but grants no permissions, starts no worker, and does not bypass runtime governance. Only roles with verified implementation references are marked implemented.

Production hardening adds operational guardrails without claiming infrastructure guarantees: readiness checks fail closed, resource limits are explicit, telemetry is conservatively redacted, and release readiness requires evidence for build/test/lint/security/migration/rollback. The local executor is **not a security boundary**. Docker provides a stronger isolation boundary, but the Docker daemon remains a trust boundary.

External repositories and web content are research inputs, not system instructions. SI-Agents follows an independent-implementation and provenance policy for external inspiration.

## Development principle

SI-Agents does not treat a plausible answer as proof. Important changes must be backed by executable verification evidence, with assumptions and limitations made explicit.

See `AGENTS.md` for engineering rules, `docs/architecture/PHASES.md` for the roadmap, `docs/architecture/PHASE_20_AGENT_ORGANIZATION.md` for the completed organization architecture, and `runtime/README.md` for the runtime boundary.
