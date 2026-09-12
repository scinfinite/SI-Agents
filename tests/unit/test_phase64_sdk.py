"""Phase 64 SDK, transport, pagination, auth, and subscription contracts."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

import pytest

from core.control_api.pagination import decode_cursor, encode_cursor, filter_items, paginate
from core.control_api.service import ControlApiService
from core.control_api.server import create_server
from sdk.python.si_agents import ApiException, SIClient


def test_cursor_is_bound_to_filters_and_bounded() -> None:
    params = {"q": "agent", "filter.division": "engineering"}
    cursor = encode_cursor(10, params)
    assert decode_cursor(cursor, params) == 10
    with pytest.raises(ValueError, match="does not match"):
        decode_cursor(cursor, {"q": "different"})
    with pytest.raises(ValueError):
        decode_cursor("x" * 300, params)


def test_pagination_and_filtering_are_deterministic() -> None:
    items = [{"id": "b", "name": "Beta"}, {"id": "a", "name": "Alpha"}, {"id": "c", "name": "Gamma"}]
    filtered = filter_items(items, "a", {})
    assert [item["id"] for item in filtered] == ["b", "a", "c"]
    first = paginate(items, limit=2, cursor=None, params={"q": ""})
    assert len(first["items"]) == 2 and first["next_cursor"]
    second = paginate(items, limit=2, cursor=first["next_cursor"], params={"q": ""})
    assert [item["id"] for item in second["items"]] == ["c"]


def _request(url: str, *, method: str = "GET", body: dict[str, object] | None = None, token: str | None = None) -> object:
    data = None if body is None else json.dumps(body).encode()
    headers = {"Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(url, data=data, headers=headers, method=method)
    with urlopen(request, timeout=5) as response:
        return json.loads(response.read().decode()) if response.status != 204 else None


def test_control_api_supports_auth_pagination_idempotency_and_subscription() -> None:
    root = Path(__file__).resolve().parents[2]
    service = ControlApiService(root)
    server = create_server(service, port=0, auth_token="phase64-test-token")
    server.timeout = 0.2
    thread = __import__("threading").Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        assert _request(base + "/api/v1/health")["status"] == "ok"
        with pytest.raises(Exception):
            _request(base + "/api/v1/agents?limit=2")
        page = _request(base + "/api/v1/agents?limit=2", token="phase64-test-token")
        assert set(page) == {"items", "next_cursor", "limit"}

        request = Request(base + "/api/v1/runs", data=json.dumps({"action": "read", "subject": "sdk-test"}).encode(), headers={"Content-Type": "application/json", "Authorization": "Bearer phase64-test-token", "X-Idempotency-Key": "stable-1"}, method="POST")
        with urlopen(request, timeout=5) as response:
            first = json.loads(response.read().decode())
        request = Request(base + "/api/v1/runs", data=json.dumps({"action": "read", "subject": "sdk-test"}).encode(), headers={"Content-Type": "application/json", "Authorization": "Bearer phase64-test-token", "X-Idempotency-Key": "stable-1"}, method="POST")
        with urlopen(request, timeout=5) as response:
            second = json.loads(response.read().decode())
        assert first["id"] == second["id"]

        created = _request(base + "/api/v1/subscriptions", method="POST", body={"transport": "sse", "event_types": ["approval.requested"]}, token="phase64-test-token")
        assert created["transport"] == "sse"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_python_sdk_maps_server_errors_to_stable_exception() -> None:
    def opener(request, timeout):
        from urllib.error import HTTPError
        from io import BytesIO
        raise HTTPError(request.full_url, 403, "forbidden", {}, BytesIO(b'{"error":"forbidden","message":"no","request_id":"r1"}'))

    client = SIClient(opener=opener)
    with pytest.raises(ApiException) as raised:
        client.health()
    assert raised.value.status == 403
    assert raised.value.error.request_id == "r1"
