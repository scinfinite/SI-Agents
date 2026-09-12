"""Advanced transport-neutral CLI platform for SI-Agents.

The CLI is an adapter over the Control API. It never becomes an execution,
provider, governance, or workflow authority. Local mode calls ControlApiService;
remote mode calls the existing /api/v1 HTTP surface with explicit authentication.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable

from core.control_api.service import ControlApiService

MAX_JSON = 1_048_576
MAX_ATTACHMENT = 10 * 1024 * 1024
MAX_PIPELINE = 256 * 1024
MAX_SESSIONS = 100
EXIT_OK = 0
EXIT_ERROR = 2
EXIT_AUTH = 3
EXIT_GOVERNANCE = 4

READ_ROUTES = {
    "status": "/api/v1",
    "agents": "/api/v1/agents",
    "teams": "/api/v1/teams",
    "workflows": "/api/v1/workflows",
    "organization": "/api/v1/organization",
    "skills": "/api/v1/skills",
    "memory": "/api/v1/memory",
    "governance": "/api/v1/governance",
    "evidence": "/api/v1/evidence",
    "environments": "/api/v1/environments",
    "harnesses": "/api/v1/harnesses",
    "settings": "/api/v1/settings",
    "visualization": "/api/v1/visualization",
    "events": "/api/v1/events",
    "runs": "/api/v1/runs",
}


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    return value


def _error(code: str, message: str, *, details: Any = None) -> dict[str, Any]:
    result: dict[str, Any] = {"code": code, "message": message}
    if details is not None:
        result["details"] = _json_safe(details)
    return result


def _sessions_path() -> Path:
    explicit = os.environ.get("SI_SESSIONS")
    if explicit:
        return Path(explicit).expanduser()
    return Path.home() / ".local" / "state" / "si-agents" / "sessions.json"


def _load_sessions() -> list[dict[str, Any]]:
    path = _sessions_path()
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("session store must contain a JSON array")
    return [x for x in payload if isinstance(x, dict)][-MAX_SESSIONS:]


def _save_sessions(items: list[dict[str, Any]]) -> None:
    path = _sessions_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.parent.chmod(0o700)
    data = json.dumps(items[-MAX_SESSIONS:], sort_keys=True, separators=(",", ":")) + "\n"
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(data, encoding="utf-8")
    temporary.chmod(0o600)
    temporary.replace(path)


class PlatformClient:
    """Small stable client facade with local and authenticated remote transports."""

    def __init__(self, root: Path, *, transport: str = "local", base_url: str = "", token_env: str = "SI_AUTH_TOKEN", timeout: float = 15.0) -> None:
        if transport not in {"local", "remote"}:
            raise ValueError("transport must be local or remote")
        if not 0.1 <= timeout <= 120:
            raise ValueError("timeout must be between 0.1 and 120 seconds")
        self.root = root.resolve()
        self.transport = transport
        self.base_url = base_url.rstrip("/")
        self.token_env = token_env
        self.timeout = timeout
        self.service = ControlApiService(self.root) if transport == "local" else None

    def _remote(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
        if not self.base_url:
            raise ValueError("--base-url is required for remote transport")
        token = os.environ.get(self.token_env, "").strip()
        if not token:
            raise PermissionError(f"authentication token is missing from ${self.token_env}")
        if payload is not None and len(json.dumps(payload, separators=(",", ":")).encode()) > MAX_JSON:
            raise ValueError("request exceeds 1 MiB")
        data = None if payload is None else json.dumps(payload, separators=(",", ":")).encode()
        request = urllib.request.Request(self.base_url + path, data=data, method=method, headers={"Accept": "application/json", "Authorization": f"Bearer {token}", "Content-Type": "application/json", "X-Request-ID": f"cli-{os.getpid()}-{time.time_ns()}"})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read(MAX_JSON + 1)
                if len(raw) > MAX_JSON:
                    raise ValueError("response exceeds 1 MiB")
                return json.loads(raw.decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read(MAX_JSON).decode("utf-8", errors="replace")
            try:
                details = json.loads(body)
            except json.JSONDecodeError:
                details = {"status": exc.code}
            if exc.code in {401, 403}:
                raise PermissionError(details) from exc
            raise RuntimeError(details) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"remote transport unavailable: {exc.reason}") from exc

    def get(self, name: str) -> Any:
        if self.transport == "remote":
            return self._remote("GET", READ_ROUTES[name])
        assert self.service is not None
        readers: dict[str, Callable[[], Any]] = {
            "status": lambda: self.service.snapshot().as_dict(),
            "agents": self.service.agents,
            "teams": self.service.teams,
            "workflows": self.service.workflows,
            "organization": self.service.organization,
            "skills": self.service.skills,
            "memory": self.service.memory,
            "governance": self.service.governance_state,
            "evidence": self.service.evidence,
            "environments": self.service.environments,
            "harnesses": self.service.harnesses,
            "settings": self.service.settings,
            "visualization": self.service.visualization,
            "events": self.service.events,
            "runs": self.service.runs,
        }
        return readers[name]()

    def run_create(self, payload: dict[str, Any]) -> Any:
        if self.transport == "remote":
            return self._remote("POST", "/api/v1/runs", payload)
        assert self.service is not None
        return self.service.create_run(payload)

    def run_get(self, run_id: str) -> Any:
        if self.transport == "remote":
            return self._remote("GET", "/api/v1/runs/" + _segment(run_id))
        assert self.service is not None
        return self.service.get_run(run_id)

    def approval_get(self, approval_id: str, subject: str, project: str) -> Any:
        if self.transport == "remote":
            return self._remote("GET", "/api/v1/approvals/" + _segment(approval_id))
        assert self.service is not None
        return self.service.get_approval(approval_id, subject_id=subject, project_id=project)

    def approval_list(self, subject: str, project: str, limit: int) -> Any:
        if self.transport == "remote":
            return self._remote("GET", "/api/v1/approvals")
        assert self.service is not None
        return self.service.approvals_queue(subject_id=subject, project_id=project, limit=limit)

    def approval_decide(self, approval_id: str, payload: dict[str, Any]) -> Any:
        if self.transport == "remote":
            return self._remote("POST", "/api/v1/approvals/" + _segment(approval_id) + "/decide", payload)
        assert self.service is not None
        return self.service.decide_approval(approval_id, payload)


def _segment(value: str) -> str:
    if not value or len(value) > 256 or any(ch in value for ch in "/?#%\\"):
        raise ValueError("invalid identifier")
    return value


def _filter_items(items: Any, search: str | None) -> Any:
    if not search or not isinstance(items, list):
        return items
    needle = search.casefold()
    return [item for item in items if needle in json.dumps(item, sort_keys=True, ensure_ascii=False).casefold()]


def _print_result(data: Any, *, as_json: bool, pretty: bool, command: str) -> None:
    envelope = {"ok": True, "command": command, "data": _json_safe(data)}
    if as_json or pretty:
        print(json.dumps(envelope, ensure_ascii=False, sort_keys=True, indent=2 if pretty else None, separators=None if pretty else (",", ":")))
        return
    if isinstance(data, list):
        for item in data:
            print(json.dumps(_json_safe(item), ensure_ascii=False, sort_keys=True))
    elif isinstance(data, dict):
        for key, value in data.items():
            print(f"{key}: {value}")
    else:
        print(data)


def _finish(args: argparse.Namespace, data: Any, command: str) -> int:
    _print_result(data, as_json=args.json, pretty=args.pretty, command=command)
    return EXIT_OK


def _cmd_catalog(client: PlatformClient, args: argparse.Namespace, name: str) -> int:
    return _finish(args, _filter_items(client.get(name), getattr(args, "search", None)), name)


def cmd_status(client: PlatformClient, args: argparse.Namespace) -> int:
    data = client.get("status")
    data = {"transport": client.transport, "base_url": client.base_url or None, "control_api": data}
    return _finish(args, data, "status")


def cmd_run_create(client: PlatformClient, args: argparse.Namespace) -> int:
    payload: dict[str, Any] = {"action": args.action, "subject": args.subject, "risk": args.risk, "data_class": args.data_class, "capabilities": args.capability, "provenance": args.provenance, "estimated_cost": args.estimated_cost, "external_egress": args.external_egress, "paid_resource": args.paid_resource, "destructive": args.destructive, "production": args.production, "credential": args.credential, "publication": args.publication}
    result = client.run_create(payload)
    return _finish(args, result, "run.create")


def cmd_run_list(client: PlatformClient, args: argparse.Namespace) -> int:
    return _finish(args, client.get("runs"), "run.list")


def cmd_run_get(client: PlatformClient, args: argparse.Namespace) -> int:
    return _finish(args, client.run_get(args.run_id), "run.get")


def cmd_approval_list(client: PlatformClient, args: argparse.Namespace) -> int:
    if not args.subject or not args.project:
        raise ValueError("--subject and --project are required for identity-bound approval access")
    return _finish(args, client.approval_list(args.subject, args.project, args.limit), "approval.list")


def cmd_approval_get(client: PlatformClient, args: argparse.Namespace) -> int:
    if not args.subject or not args.project:
        raise ValueError("--subject and --project are required for identity-bound approval access")
    return _finish(args, client.approval_get(args.approval_id, args.subject, args.project), "approval.get")


def cmd_approval_decide(client: PlatformClient, args: argparse.Namespace) -> int:
    payload = {"decision": args.decision, "subject_id": args.subject, "project_id": args.project, "decision_by": args.decision_by or args.subject, "reason": args.reason, "expected_revision": args.expected_revision}
    result = client.approval_decide(args.approval_id, payload)
    return _finish(args, result, "approval.decide")


def cmd_session(args: argparse.Namespace) -> int:
    sessions = _load_sessions()
    if args.session_command == "start":
        item = {"id": hashlib.sha256(f"{time.time_ns()}:{args.name}".encode()).hexdigest()[:24], "name": args.name, "transport": args.transport, "base_url": args.base_url or None, "workspace": str(Path(args.root).resolve()), "created_at": int(time.time())}
        sessions.append(item)
        _save_sessions(sessions)
        return _finish(args, item, "session.start")
    if args.session_command == "list":
        return _finish(args, sessions, "session.list")
    for item in sessions:
        if item.get("id") == args.session_id:
            return _finish(args, item, "session.get")
    raise KeyError(args.session_id)


def cmd_attachment(args: argparse.Namespace) -> int:
    path = Path(args.path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    size = path.stat().st_size
    if size > MAX_ATTACHMENT:
        raise ValueError("attachment exceeds 10 MiB safety limit")
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(64 * 1024), b""):
            digest.update(chunk)
    data = {"path": str(path), "name": path.name, "size": size, "sha256": digest.hexdigest(), "media_type": mimetypes.guess_type(path.name)[0] or "application/octet-stream"}
    return _finish(args, data, "attachment.inspect")


def cmd_auth(args: argparse.Namespace) -> int:
    present = bool(os.environ.get(args.token_env, "").strip())
    data = {"token_env": args.token_env, "configured": present, "secret_persisted": False, "note": "tokens are read from the environment and are never printed or persisted by the CLI"}
    return _finish(args, data, "auth.status")


def cmd_config(args: argparse.Namespace) -> int:
    allowed = {"transport", "base_url", "token_env", "root", "timeout"}
    path = Path(args.path).expanduser() if args.path else Path.home() / ".config" / "si-agents" / "cli.json"
    payload: dict[str, Any] = {}
    if path.exists():
        loaded = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise ValueError("CLI config must be a JSON object")
        unknown = set(loaded) - allowed
        if unknown:
            raise ValueError("unknown CLI config keys: " + ", ".join(sorted(unknown)))
        payload = loaded
    if args.config_command == "get":
        return _finish(args, payload, "config.get")
    if args.key not in allowed or args.key == "token_env" and not args.value:
        raise ValueError("invalid config key or value")
    if args.key == "token_env" and any(ch in args.value for ch in " \t\n"):
        raise ValueError("token environment variable name must not contain whitespace")
    payload[args.key] = args.value
    path.parent.mkdir(parents=True, exist_ok=True)
    path.parent.chmod(0o700)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    path.chmod(0o600)
    return _finish(args, {"path": str(path), "key": args.key, "value": args.value}, "config.set")


def cmd_models(client: PlatformClient, args: argparse.Namespace) -> int:
    if client.transport == "remote":
        return _finish(args, client._remote("GET", "/v1/models"), "models.list")
    settings = client.get("settings")
    return _finish(args, {"authority": "OmniRoute", "transport": "local", "configured_model": settings["execution"].get("run_creation") if isinstance(settings, dict) else None, "note": "provider/model discovery belongs to OmniRoute; SI Core does not invent a local catalog"}, "models.list")


def cmd_providers(client: PlatformClient, args: argparse.Namespace) -> int:
    if client.transport == "remote":
        return _finish(args, client._remote("GET", "/v1/providers"), "providers.list")
    return _finish(args, {"authority": "OmniRoute", "transport": "local", "providers": [], "note": "provider discovery is delegated to OmniRoute"}, "providers.list")


def cmd_stream(client: PlatformClient, args: argparse.Namespace) -> int:
    deadline = time.monotonic() + args.timeout
    events: list[Any] = []
    while True:
        run = client.run_get(args.run_id)
        events.append({"type": "run.state", "run": run, "timestamp": time.time()})
        if args.once or str(run.get("status", "")).lower() not in {"queued", "running", "waiting", "paused"}:
            break
        if time.monotonic() >= deadline or len(events) >= args.max_events:
            break
        time.sleep(args.interval)
    return _finish(args, events, "stream.run")


def cmd_resume(client: PlatformClient, args: argparse.Namespace) -> int:
    run = client.run_get(args.run_id)
    status = str(run.get("status", "")).lower()
    if status not in {"paused", "waiting"}:
        raise ValueError(f"run {args.run_id} is not resumable from status {status or 'unknown'}")
    raise RuntimeError("resume authority belongs to the downstream execution engine; CLI cannot bypass it")


def cmd_pipeline(client: PlatformClient, args: argparse.Namespace) -> int:
    path = Path(args.path).expanduser().resolve()
    raw = path.read_bytes()
    if len(raw) > MAX_PIPELINE:
        raise ValueError("pipeline file exceeds 256 KiB")
    payload = json.loads(raw.decode("utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("steps"), list):
        raise ValueError("pipeline must be an object with a steps array")
    if not 1 <= len(payload["steps"]) <= 100:
        raise ValueError("pipeline must contain 1-100 steps")
    results = []
    for index, step in enumerate(payload["steps"]):
        if not isinstance(step, dict) or not isinstance(step.get("action"), str) or not isinstance(step.get("subject"), str):
            raise ValueError(f"pipeline step {index + 1} requires action and subject")
        result = client.run_create(dict(step))
        results.append({"index": index, "result": result})
    return _finish(args, {"steps": results, "count": len(results), "authority": "SI Core governance per step"}, "pipeline.run")


def _common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--root", default=".")
    parser.add_argument("--transport", choices=("local", "remote"), default="local")
    parser.add_argument("--base-url", default="")
    parser.add_argument("--token-env", default="SI_AUTH_TOKEN")
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--json", action="store_true", help="emit one stable JSON envelope")
    parser.add_argument("--pretty", action="store_true", help="pretty-print the JSON envelope")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="si", description="SI-Agents Phase 68 advanced CLI platform")
    _common(parser)
    sub = parser.add_subparsers(dest="command", required=True)

    status = sub.add_parser("status"); status.set_defaults(handler=cmd_status)
    for name in ("agents", "teams", "workflows"):
        item = sub.add_parser(name); item.add_argument("--search"); item.set_defaults(handler=lambda c, a, n=name: _cmd_catalog(c, a, n))
    for name in ("organization", "skills", "memory", "governance", "evidence", "environments", "harnesses", "settings", "visualization", "events"):
        item = sub.add_parser(name); item.set_defaults(handler=lambda c, a, n=name: _cmd_catalog(c, a, n))

    run = sub.add_parser("run"); run_sub = run.add_subparsers(dest="run_command", required=True)
    create = run_sub.add_parser("create"); create.add_argument("action"); create.add_argument("subject"); create.add_argument("--risk", default="low"); create.add_argument("--data-class", default="public"); create.add_argument("--capability", action="append", default=[]); create.add_argument("--provenance", action="append", default=[]); create.add_argument("--estimated-cost", type=float, default=0.0); create.add_argument("--external-egress", action="store_true"); create.add_argument("--paid-resource", action="store_true"); create.add_argument("--destructive", action="store_true"); create.add_argument("--production", action="store_true"); create.add_argument("--credential", action="store_true"); create.add_argument("--publication", action="store_true"); create.set_defaults(handler=cmd_run_create)
    listed = run_sub.add_parser("list"); listed.set_defaults(handler=cmd_run_list)
    got = run_sub.add_parser("get"); got.add_argument("run_id"); got.set_defaults(handler=cmd_run_get)

    for name, source in (("task", "run"), ("execution", "run")):
        item = sub.add_parser(name); item_sub = item.add_subparsers(dest="item_command", required=True)
        li = item_sub.add_parser("list"); li.set_defaults(handler=cmd_run_list)
        ge = item_sub.add_parser("get"); ge.add_argument("run_id"); ge.set_defaults(handler=cmd_run_get)
        if name == "task":
            cr = item_sub.add_parser("create"); cr.add_argument("action"); cr.add_argument("subject"); cr.add_argument("--risk", default="low"); cr.add_argument("--data-class", default="public"); cr.add_argument("--estimated-cost", type=float, default=0.0); cr.add_argument("--external-egress", action="store_true"); cr.add_argument("--destructive", action="store_true"); cr.set_defaults(handler=cmd_run_create)

    approval = sub.add_parser("approval"); approval_sub = approval.add_subparsers(dest="approval_command", required=True)
    al = approval_sub.add_parser("list"); al.add_argument("--subject", required=True); al.add_argument("--project", required=True); al.add_argument("--limit", type=int, default=100); al.set_defaults(handler=cmd_approval_list)
    ag = approval_sub.add_parser("get"); ag.add_argument("approval_id"); ag.add_argument("--subject", required=True); ag.add_argument("--project", required=True); ag.set_defaults(handler=cmd_approval_get)
    ad = approval_sub.add_parser("decide"); ad.add_argument("approval_id"); ad.add_argument("decision", choices=("approved", "rejected", "expired")); ad.add_argument("--subject", required=True); ad.add_argument("--project", required=True); ad.add_argument("--decision-by"); ad.add_argument("--reason", default=""); ad.add_argument("--expected-revision", type=int); ad.set_defaults(handler=cmd_approval_decide)

    session = sub.add_parser("session"); ss = session.add_subparsers(dest="session_command", required=True)
    st = ss.add_parser("start"); st.add_argument("name"); st.set_defaults(handler=cmd_session)
    sl = ss.add_parser("list"); sl.set_defaults(handler=cmd_session)
    sg = ss.add_parser("get"); sg.add_argument("session_id"); sg.set_defaults(handler=cmd_session)

    attach = sub.add_parser("attachment"); attach_sub = attach.add_subparsers(dest="attachment_command", required=True); ai = attach_sub.add_parser("inspect"); ai.add_argument("path"); ai.set_defaults(handler=cmd_attachment)
    auth = sub.add_parser("auth"); auth_sub = auth.add_subparsers(dest="auth_command", required=True); ast = auth_sub.add_parser("status"); ast.set_defaults(handler=cmd_auth)
    config = sub.add_parser("config"); cs = config.add_subparsers(dest="config_command", required=True); cg = cs.add_parser("get"); cg.add_argument("--path"); cg.set_defaults(handler=cmd_config); cset = cs.add_parser("set"); cset.add_argument("key", choices=("transport", "base_url", "token_env", "root", "timeout")); cset.add_argument("value"); cset.add_argument("--path"); cset.set_defaults(handler=cmd_config)
    models = sub.add_parser("models"); models_sub = models.add_subparsers(dest="models_command", required=True); ml = models_sub.add_parser("list"); ml.set_defaults(handler=cmd_models)
    providers = sub.add_parser("providers"); providers_sub = providers.add_subparsers(dest="providers_command", required=True); pl = providers_sub.add_parser("list"); pl.set_defaults(handler=cmd_providers)
    stream = sub.add_parser("stream"); stream.add_argument("run_id"); stream.add_argument("--interval", type=float, default=0.5); stream.add_argument("--timeout", type=float, default=10.0); stream.add_argument("--max-events", type=int, default=100); stream.add_argument("--once", action="store_true"); stream.set_defaults(handler=cmd_stream)
    resume = sub.add_parser("resume"); resume.add_argument("run_id"); resume.set_defaults(handler=cmd_resume)
    pipeline = sub.add_parser("pipeline"); pipeline_sub = pipeline.add_subparsers(dest="pipeline_command", required=True); pr = pipeline_sub.add_parser("run"); pr.add_argument("path"); pr.set_defaults(handler=cmd_pipeline)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        client = PlatformClient(Path(args.root), transport=args.transport, base_url=args.base_url, token_env=args.token_env, timeout=args.timeout)
        return args.handler(client, args)
    except PermissionError as exc:
        payload = {"ok": False, "command": getattr(args, "command", "unknown"), "error": _error("AUTHENTICATION_REQUIRED", str(exc))}
        print(json.dumps(payload, sort_keys=True), file=sys.stderr)
        return EXIT_AUTH
    except RuntimeError as exc:
        payload = {"ok": False, "command": getattr(args, "command", "unknown"), "error": _error("REQUEST_FAILED", str(exc))}
        print(json.dumps(payload, sort_keys=True), file=sys.stderr)
        return EXIT_GOVERNANCE if "govern" in str(exc).lower() else EXIT_ERROR
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        payload = {"ok": False, "command": getattr(args, "command", "unknown"), "error": _error("INVALID_REQUEST", str(exc))}
        print(json.dumps(payload, sort_keys=True), file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
