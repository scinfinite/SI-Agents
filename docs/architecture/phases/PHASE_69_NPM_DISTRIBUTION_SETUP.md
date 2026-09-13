# Phase 69 — npm Distribution + Setup

**Status: Complete / 100% implementation closed pending final mainline CI evidence.**

## Scope

Phase 69 adds npm as a distribution/bootstrap surface without creating a second SI runtime authority.

### Delivered

- Root `package.json` with npm metadata, Apache-2.0 license, Node 18+ engine, and `si-agents` executable.
- Cross-platform `bin/si-agents.js` launcher.
- Existing Python `core.cli.dispatch` remains the authoritative runtime and command router.
- Python discovery supports `python3`/`python` on Unix-like hosts and `python`/`py` on Windows.
- `SI_AGENTS_PYTHON` allows an explicit Python executable override.
- `si-agents setup` explicitly bootstraps the matching `si-agents` Python package when the runtime is unavailable.
- Clear prerequisite/error behavior instead of silently installing or invoking a shell.
- npm package content is allowlisted to the launcher, license/notice metadata, and npm usage guide.
- Version and license consistency checks are automated.
- npm tarball contents are verified with `npm pack` and a deterministic allowlist.
- Launcher `--version` and `help` smoke checks are automated.
- CI runs npm verification alongside the existing Python packaging, audit, integration, lint, compile, and pytest gates.
- Termux behavior remains governed by the existing Python capacity/heavy-workload policy; the npm layer does not bypass it.

## Authority boundary

`si-agents` is a thin launcher/bootstrapper. It does not own execution, authorization, provider routing, sessions, workspaces, or agent catalogs. Those remain SI Core/runtime responsibilities.

## Publication boundary

Phase 69 prepares and verifies the npm package but does not publish it automatically. Registry publication requires the maintainer's explicit npm account/registry authentication and release action.

## Acceptance

- `npm run verify` validates package metadata, Python-version parity, required distribution files, tarball contents, and launcher smoke behavior.
- CI must be green on the exact mainline tree after all Phase 69 documentation and implementation changes.
- npm publication is a maintainer-controlled release operation and is not required to prove the source implementation itself is complete.
