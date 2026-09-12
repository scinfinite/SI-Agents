import json
import threading
import urllib.request
from datetime import UTC, datetime, timedelta
from pathlib import Path

from core.control_api.server import create_server
from core.control_api.service import ControlApiService


def _request(server, method, path, body=None, subject="u1", project="p1"):
    payload = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(
        f"http://127.0.0.1:{server.server_port}{path}",
        data=payload,
        method=method,
        headers={
            "Content-Type": "application/json",
            "X-SI-Subject": subject,
            "X-SI-Project": project,
        },
    )
    with urllib.request.urlopen(request, timeout=3) as response:
        return response.status, json.loads(response.read())


def test_wait_control_api_round_trip_and_isolation(tmp_path: Path):
    server = create_server(ControlApiService(tmp_path), host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        wake_at = (datetime.now(UTC) - timedelta(seconds=1)).isoformat()
        status, created = _request(server, "POST", "/api/v1/waits", {
            "kind": "timer", "wake_at": wake_at, "payload": {"usage": {"input_tokens": 2}},
        })
        assert status == 201
        wait_id = created["wait_id"]

        status, listing = _request(server, "GET", "/api/v1/waits")
        assert status == 200 and listing[0]["wait_id"] == wait_id

        status, claimed = _request(server, "POST", f"/api/v1/waits/{wait_id}/claim", {"limit": 1})
        assert status == 200 and claimed[0]["state"] == "claimed"

        status, completed = _request(server, "POST", f"/api/v1/waits/{wait_id}/complete", {"expected_revision": claimed[0]["revision"]})
        assert status == 200 and completed["state"] == "completed"

        try:
            _request(server, "GET", f"/api/v1/waits/{wait_id}", subject="u2")
            raise AssertionError("cross-subject access should fail")
        except urllib.error.HTTPError as exc:
            assert exc.code == 404
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
