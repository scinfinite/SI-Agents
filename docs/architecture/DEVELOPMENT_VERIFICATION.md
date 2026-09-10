# Development Verification

SI-Agents uses one deterministic verification contract locally and in CI. The goal is to prevent tool-version drift and catch the same classes of failures before they reach a phase branch or `main`.

## Pinned toolchain

`requirements-dev.txt` pins the build, pytest, Ruff, setuptools, wheel, and pre-commit versions. `.github/workflows/ci.yml` installs this exact file instead of resolving floating lint/test versions.

`pyproject.toml` also pins Ruff with `required-version`, and pytest uses strict configuration and marker handling.

Do not casually upgrade these tools. Upgrade them deliberately, run the complete verification suite, and record the reason in the change.

## Local verification

Run:

```bash
bash scripts/verify.sh
```

The script performs:

1. deterministic development-tool installation;
2. distribution build;
3. Ruff linting;
4. Python bytecode compilation for runtime packages;
5. strict pytest execution;
6. SI repository audit.

A successful run ends with `SI verification: PASS`.

## Pre-commit protection

`.pre-commit-config.yaml` uses the same pinned Ruff release and runs Ruff check/format hooks before commits. Install once with:

```bash
python -m pip install -r requirements-dev.txt
pre-commit install
```

Then normal commits receive automatic Ruff corrections and formatting checks before the commit is created.

## CI gates

Every push and pull request runs:

- pinned dependency installation;
- distribution build;
- isolated wheel installation/import/CLI smoke tests;
- SI repository audit;
- Ruff lint;
- Python compilation;
- strict pytest;
- diagnostic artifact upload on failure.

Repository-wide Ruff formatting is intentionally not a separate CI failure gate because historical files are not uniformly formatter-normalized. Formatting is handled by the pre-commit hook and can be adopted incrementally without making unrelated formatting drift block functional verification.

## Why this prevents recurring failures

The previous recurring pattern was caused by a combination of source-level lint violations and floating development-tool behavior. The repository now has:

- explicit source fixes for the known Ruff `E702` semicolon violations;
- one pinned Ruff version in local and CI environments;
- one pinned pytest/build toolchain;
- strict pytest configuration;
- compile-time checks before tests;
- an isolated wheel smoke test;
- a single local verification command matching the CI gates;
- pre-commit automation for Ruff before commits.

If a future tool upgrade introduces a new failure, it must be treated as a deliberate toolchain migration rather than an accidental CI surprise.
