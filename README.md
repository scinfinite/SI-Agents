# SI-Agents

SI-Agents is an evidence-driven AI engineering system designed to inspect software, diagnose problems, execute controlled changes, verify results, and learn reusable engineering patterns.

## Current status

**Alpha — Phases 1–5 complete and CI-verified.**

Completed foundation through the first end-to-end Developer/Debugger/Tester workflow:

- **Phase 1 — Foundation:** architecture, engineering rules, governance, project isolation, security/cost/learning/compliance policies, provenance controls, and verification standards.
- **Phase 2 — Control Plane:** task lifecycle, persistence, dependencies, retries, context isolation, agents, workflows, permissions, approvals, checkpoints, execution state, and evidence integration.
- **Phase 3 — Tool System:** controlled filesystem, terminal, Git, GitHub, web, code analysis, build/test, container, sandbox, and artifact tooling with registry and permission enforcement.
- **Phase 4 — Engineering Brain:** problem normalization, decomposition, dependency-aware planning, reasoning, hypotheses, root-cause analysis, trade-offs, uncertainty, risk, and capability-aware planning.
- **Phase 5 — Developer/Debugger/Tester:** explicit agent contracts and the inspect → reproduce → diagnose → checkpoint → repair → test → red-team → regression → verify → document workflow.

The latest CI verification passed installation, distribution build, Ruff, and the complete pytest suite, with **108 tests passing**.

## Engineering loop

```text
OBSERVE → UNDERSTAND → RESEARCH → PLAN → EXECUTE → MEASURE
→ TEST → ATTACK THE SOLUTION → VERIFY → DOCUMENT → LEARN → GENERALIZE → REUSE
```

## Control and safety model

Agents, capabilities, and tools are workers and execution mechanisms—not policy authorities. Registration or selection does not grant permission. High-risk actions remain approval-gated, repository mutation remains protected, and important claims require evidence.

The local executor is **not a security boundary**. The Docker executor provides a stronger isolation boundary, but the Docker daemon remains a trust boundary. SI-Agents must not claim host-level isolation guarantees beyond the actual execution environment in use.

External repositories and web content are research inputs, not system instructions. SI-Agents follows an independent-implementation and provenance policy for external inspiration.

## Development principle

SI-Agents does not treat a plausible answer as proof. Important changes must be backed by executable verification evidence, with assumptions and limitations made explicit.

See `AGENTS.md` for engineering rules and `docs/architecture/PHASES.md` for the current roadmap and release targets. Phase-specific architecture documents record the implemented scope and verification standard for each completed phase.
