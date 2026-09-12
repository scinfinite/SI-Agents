# Phase 68 — Advanced CLI Platform

**Status:** Implementation complete pending final synchronized-tree closure gate.

## Authority

The CLI is a client/adapter over SI Core and the existing Control API. It does not own execution, workflow state, governance, approvals, provider routing, credentials, or downstream lifecycle. OmniRoute remains the model/provider/API routing authority.

```text
User / automation
      ↓
   `si` CLI
      ↓
 local ControlApiService OR authenticated Control API HTTP
      ↓
 SI Core governance / lifecycle / execution authority
      ↓
 scheduler / orchestrator / downstream runtime
      ↓
 OmniRoute → models / providers / APIs
```

## Advanced surface

Phase 68 adds a deterministic, machine-friendly platform surface:

- `run create/list/get` — governed run creation and inspection;
- `task create/list/get` — task-oriented aliases over governed run records;
- `agent`, `team`, `workflow` — canonical resource navigation;
- `execution` — execution-state inspection without claiming downstream authority;
- `approval list/get/decide` — identity-bound human approval controls;
- `session start/list/get` — bounded client session metadata;
- `resume` — fail-closed handoff to downstream resume authority;
- `events`, `logs`, `stream` — bounded event/state observation;
- `models`, `providers` — discovery delegated to OmniRoute;
- `attachment inspect` — bounded metadata/hash inspection without arbitrary upload execution;
- `config`, `profile`, `auth` — non-secret client configuration, transport profiles, and environment-token status;
- `pipeline run` — bounded declarative submission with per-step SI Core governance;
- `status`, `organization`, `skills`, `memory`, `governance`, `evidence`, `environments`, `harnesses`, `settings`, and `visualization` read surfaces.

## Transport contract

### Local

Local mode instantiates `ControlApiService` directly. This is an adapter optimization; it does not create a second authority.

### Remote

Remote mode uses authenticated HTTP against the existing `/api/v1` Control API. Requests are bounded to 1 MiB, identifiers are path-safe, authentication is bearer-token based, and credentials are read from an environment variable rather than persisted by the CLI.

## Output and exit contract

`--json` emits a stable envelope:

```json
{"ok":true,"command":"run.create","data":{}}
```

Failures use machine-readable error objects and deterministic exit classes:

- `0` success;
- `2` invalid request / transport / operational failure;
- `3` authentication required or rejected;
- `4` governance or authority rejection.

Human-readable output remains available when `--json` is omitted.

## Safety invariants

- no arbitrary shell execution;
- no direct provider/model execution authority;
- no credential printing or secret persistence;
- no bypass of SI Core governance for run creation;
- identity and project boundaries are required for approval operations;
- attachment inspection is bounded to 10 MiB;
- pipeline files are bounded to 256 KiB and 100 steps;
- session metadata is bounded to 100 records;
- profile count is bounded to 32 and profile data is non-secret transport metadata only;
- remote request/response payloads are bounded to 1 MiB;
- run streaming is bounded by timeout/event count;
- resume is fail-closed when downstream execution owns the resume transition;
- unknown or malformed inputs fail without shell interpretation.

## Verification

Coverage is in `tests/test_phase68_cli.py` and existing Control API/TUI/Web suites. Closure requires the full repository CI gate, including wheel installation, repository audit, integration verification, Ruff, full pytest, SDK workflow, documentation synchronization, merge, and final exact-tree mainline CI.
