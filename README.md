# SI-Agents

SI-Agents is an evidence-driven AI engineering system designed to inspect software, diagnose problems, execute controlled changes, verify results, and learn reusable engineering patterns.

## Engineering loop

```text
OBSERVE → UNDERSTAND → RESEARCH → PLAN → EXECUTE → MEASURE
→ TEST → ATTACK THE SOLUTION → VERIFY → DOCUMENT → LEARN → GENERALIZE → REUSE
```

## Current status

**Alpha — foundation, control plane, and execution boundaries**

The repository currently provides:

- evidence-first engineering rules and governance configuration;
- task lifecycle management;
- immutable control-plane checkpoints;
- optional filesystem-backed checkpoints with approval-gated restore;
- a backend-neutral command runner;
- a development-only local executor with a conservative command-policy gate;
- a Docker execution backend with disabled networking, reduced Linux privileges, read-only container root, and resource limits;
- verification evidence primitives;
- an ordered Alpha repair workflow for inspection, reproduction, checkpointing, repair, verification, red-team checks, and regression checks;
- automated package build, lint, and test verification through GitHub Actions.

The local executor is **not a security boundary**. The Docker executor is a stronger isolation boundary, but the Docker daemon remains a trust boundary. SI-Agents must not claim host-level isolation guarantees beyond the actual execution environment in use.

## Development principle

SI-Agents does not treat a plausible answer as proof. Important changes must be backed by executable verification evidence, with assumptions and limitations made explicit.

See `AGENTS.md` for the engineering rules, `docs/architecture/PHASES.md` for the implementation roadmap, `docs/architecture/CONTROL_PLANE.md` for the control-plane contract, and `docs/architecture/EXECUTION_BACKENDS.md` for execution-boundary details.
