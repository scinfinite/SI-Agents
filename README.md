# SI-Agents

SI-Agents is an evidence-driven AI engineering system designed to inspect software, diagnose problems, execute controlled changes, verify results, and learn reusable engineering patterns.

## Engineering loop

```text
OBSERVE → UNDERSTAND → RESEARCH → PLAN → EXECUTE → MEASURE
→ TEST → ATTACK THE SOLUTION → VERIFY → DOCUMENT → LEARN → GENERALIZE → REUSE
```

## Current status

**Alpha — foundation and control-plane development**

The repository currently provides:

- evidence-first engineering rules and governance configuration;
- task lifecycle management;
- immutable control-plane checkpoints;
- local command execution with an explicit conservative policy gate;
- verification evidence primitives;
- automated package build, lint, and test verification through GitHub Actions.

The local executor is intentionally **not a security boundary**. Safe execution of untrusted projects requires OS/container isolation and additional resource, network, filesystem, and process controls.

## Development principle

SI-Agents does not treat a plausible answer as proof. Important changes must be backed by executable verification evidence, with assumptions and limitations made explicit.

See `AGENTS.md` for the engineering rules and `docs/architecture/PHASES.md` for the implementation roadmap.
