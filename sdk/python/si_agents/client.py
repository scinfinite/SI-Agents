"""Small dependency-free Python client with stable typed contracts."""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, Callable, Iterator, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen

API_VERSION = "v1"


@dataclass(frozen=True, slots=True)
class ApiError:
    code: str
    message: str
    request_id: str


class ApiException(RuntimeError):
    """Stable API failure carrying HTTP status and server error identity."""

    def __init__(self, error: ApiError, *, status: int):
        super().__init__(f"{error.code}: {error.message}")
        self.error = error
        self.status = status


@dataclass(frozen=True, slots=True)
class Page:
    items: tuple[Mapping[str, Any], ...]
    next_cursor: str | None
    limit: int


@dataclass(frozen=True, slots=True)
class Run:
    id: str
    action: str
    status: str
    subject: str


@dataclass(frozen=True, slots=True)
class Event:
    id: str
    event_type: str
    subject: str
    timestamp: str
    metadata: Mapping[str, str]


@dataclass(frozen=True, slots=True)
class Subscription:
    id: str
    event_types: tuple[str, ...]
    subject: str | None
    transport: str
    status: str


class SIClient:
    """Thread-safe client for REST plus SSE/WebSocket subscription URLs."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8787",
        *,
        token: str | None = None,
        subject: str | None = None,
        project: str | None = None,
        timeout: float = 15.0,
        opener: Callable[..., Any] = urlopen,
    ) -> None:
        self.base_url = base_url.rstrip("/") + "/"
        self.token = token
        self.subject = subject
        self.project = project
        self.timeout = timeout
        self._opener = opener

    def _url(self, path: str, params: Mapping[str, object] | None = None) -> str:
        path = path.lstrip("/")
        url = urljoin(self.base_url, path)
        if params:
            clean = {k: str(v) for k, v in params.items() if v is not None}
            if clean:
                url += ("&" if "?" in url else "?") + urlencode(clean)
        return url

    def _headers(self, *, idempotency_key: str | None = None) -> dict[str, str]:
        headers = {"Accept": "application/json", "User-Agent": "si-agents-python-sdk/0.1"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if self.subject:
            headers["X-SI-Subject"] = self.subject
        if self.project:
            headers["X-SI-Project"] = self.project
        if idempotency_key:
            headers["X-Idempotency-Key"] = idempotency_key
        return headers

    def request(self, method: str, path: str, body: Mapping[str, object] | None = None, *, idempotency_key: str | None = None) -> Any:
        payload = None if body is None else json.dumps(body, separators=(",", ":")).encode()
        headers = self._headers(idempotency_key=idempotency_key)
        if payload is not None:
            headers["Content-Type"] = "application/json"
        request = Request(self._url(path), data=payload, headers=headers, method=method.upper())
        try:
            with self._opener(request, timeout=self.timeout) as response:
                raw = response.read()
                return json.loads(raw.decode("utf-8")) if raw else None
        except HTTPError as exc:
            raw = exc.read()
            try:
                payload = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                payload = {}
            error = ApiError(str(payload.get("error", "http_error")), str(payload.get("message", exc.reason)), str(payload.get("request_id", "")))
            raise ApiException(error, status=exc.code) from exc
        except URLError as exc:
            raise ApiException(ApiError("transport_error", str(exc.reason), ""), status=0) from exc

    def health(self) -> Mapping[str, Any]:
        return self.request("GET", f"/api/{API_VERSION}/health")

    def snapshot(self) -> Mapping[str, Any]:
        return self.request("GET", f"/api/{API_VERSION}")

    def list(self, resource: str, *, limit: int = 100, cursor: str | None = None, query: str | None = None, filters: Mapping[str, str] | None = None) -> Page:
        if not 1 <= limit <= 1000:
            raise ValueError("limit must be between 1 and 1000")
        params: dict[str, object] = {"limit": limit, "cursor": cursor, "q": query}
        if filters:
            for key, value in filters.items():
                if not key or key.startswith("_"):
                    raise ValueError("filter names must be non-empty and public")
                params[f"filter.{key}"] = value
        result = self.request("GET", self._url(f"/api/{API_VERSION}/{resource}", params).removeprefix(self.base_url), None)
        if not isinstance(result, dict) or "items" not in result:
            items = result if isinstance(result, list) else []
            return Page(tuple(items), None, len(items))
        return Page(tuple(result["items"]), result.get("next_cursor"), int(result.get("limit", limit)))

    def paginate(self, resource: str, *, page_size: int = 100, query: str | None = None, filters: Mapping[str, str] | None = None) -> Iterator[Mapping[str, Any]]:
        cursor = None
        while True:
            page = self.list(resource, limit=page_size, cursor=cursor, query=query, filters=filters)
            yield from page.items
            cursor = page.next_cursor
            if not cursor:
                return

    def create_run(self, payload: Mapping[str, object], *, idempotency_key: str | None = None) -> Mapping[str, Any]:
        return self.request("POST", f"/api/{API_VERSION}/runs", payload, idempotency_key=idempotency_key)

    def get_run(self, run_id: str) -> Mapping[str, Any]:
        return self.request("GET", f"/api/{API_VERSION}/runs/{run_id}")

    def events(self, **kwargs: object) -> Page:
        return self.list("events", **kwargs)

    def subscribe_sse_url(self, *, after: int | None = None) -> str:
        return self._url(f"/api/{API_VERSION}/events/stream", {"after": after})

    def iter_sse(self, *, after: int = 0) -> Iterator[Event]:
        request = Request(self.subscribe_sse_url(after=after), headers=self._headers(), method="GET")
        response = self._opener(request, timeout=self.timeout)
        try:
            current: dict[str, str] = {}
            while True:
                line = response.readline().decode("utf-8").rstrip("\r\n")
                if not line:
                    if "data" in current:
                        payload = json.loads(current["data"])
                        yield Event(payload["id"], payload["event_type"], payload["subject"], payload["timestamp"], payload.get("metadata", {}))
                    current = {}
                    continue
                if line.startswith(":"):
                    continue
                key, _, value = line.partition(":")
                if key == "data":
                    current["data"] = value.lstrip()
        finally:
            response.close()

    def subscribe(self, *, event_types: tuple[str, ...] = (), subject: str | None = None, transport: str = "sse", target: str | None = None) -> Mapping[str, Any]:
        if transport not in {"sse", "webhook"}:
            raise ValueError("transport must be sse or webhook")
        return self.request("POST", f"/api/{API_VERSION}/subscriptions", {"event_types": list(event_types), "subject": subject, "transport": transport, "target": target})

    def map_concurrent(self, calls: list[Callable[[], Any]], *, max_concurrency: int = 8) -> list[Any]:
        if not 1 <= max_concurrency <= 32:
            raise ValueError("max_concurrency must be between 1 and 32")
        with ThreadPoolExecutor(max_workers=max_concurrency) as pool:
            return list(pool.map(lambda call: call(), calls))
