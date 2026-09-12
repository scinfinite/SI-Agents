# Phase 58 — Workspace / Worktree Lifecycle

**Status:** In implementation; final closure is gated on synchronized-tree mainline CI.

## Authority

Phase 58 establishes an isolation-first workspace lifecycle authority inside SI Core. Workspace state, ownership, locks, snapshots, diffs, artifacts, recovery, and cleanup are durable SI state. Git is an execution mechanism and never a competing business authority.

## Advanced contracts

- tenant/project-scoped workspace records with fail-closed cross-scope access
- optimistic revision control for concurrent lifecycle mutation
- bounded lease locks with owner-only heartbeat/release semantics
- directory and Git worktree materialization through an injected Git execution boundary
- branch lifecycle, base-reference tracking, deterministic diff and merge preparation
- SHA-256 snapshot and diff-artifact evidence with size/count limits
- explicit approval plus caller-owned live lock for merge authorization
- approved snapshot-based resume without restoring execution authority
- cleanup refusal for dirty/conflicted state, explicit approval for force cleanup
- path containment and symlink defenses for snapshot/cleanup operations
- tamper-evident hash-chained workspace lifecycle events
- bounded garbage-collection candidate discovery for archived/recovery state

## Authority boundaries

The workspace service does not grant capabilities, credentials, provider access, or execution identity. A merge preparation is inspection-only. A resume is a lifecycle transition; downstream execution must independently authorize any resumed work.

## Verification

tests/test_phase58_workspace.py covers scope isolation, lock contention and heartbeat, optimistic revisions, secret-like metadata rejection, symlink rejection, Git materialization, diff artifacts, branch creation, merge preparation, approval/lock requirements, cleanup, and garbage-collection discovery.

The phase closure gate additionally requires repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, documentation synchronization, and final exact-tree mainline CI.
