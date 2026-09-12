from __future__ import annotations

import json
import tempfile
import threading
import time
from http.client import HTTPConnection
from pathlib import Path

import pytest

from core.control_api.server import create_server
from core.control_api.service import ControlApiService
from core.hitl import ApprovalState, HumanApprovalService


def test_approval_lifecycle_is_identity_bound_and_audited() -> None:
    with tempfile.TemporaryDirectory() as directory:
        store = HumanApprovalService(Path(directory) / "approvals.sqlite3")
        request = store.create({"subject_id": "alice", "project_id": "p1", "kind": "approval", "gate": "deployment", "action": "deploy", "summary": "production deploy", "requested_by": "alice", "risk": "critical", "estimated_cost": 2.5, "deployment": True, "expires_in": 300})
        assert request.state is ApprovalState.PENDING
        with pytest.raises(PermissionError):
            store.get(request.approval_id, subject_id="bob", project_id="p1")
        decision = store.decide(request.approval_id, subject_id="alice", project_id="p1", decision=ApprovalState.APPROVED, decision_by="alice", reason="reviewed")
        assert decision.state is ApprovalState.APPROVED
        assert len(store.events(request.approval_id, subject_id="alice", project_id="p1")) == 2
        with pytest.raises(ValueError, match="no longer pending"):
            store.decide(request.approval_id, subject_id="alice", project_id="p1", decision=ApprovalState.RETRY, decision_by="alice", reason="again")
        store.close()


def test_decision_payload_supports_controlled_modify_retry_reassign_alternative() -> None:
    with tempfile.TemporaryDirectory() as directory:
        store = HumanApprovalService(Path(directory) / "approvals.sqlite3")
        for decision in (ApprovalState.MODIFIED, ApprovalState.RETRY, ApprovalState.REASSIGNED, ApprovalState.ALTERNATIVE):
            request = store.create({"subject_id": "alice", "project_id": "p1", "kind": "review", "gate": "risk", "action": "act", "summary": "review", "requested_by": "alice"})
            result = store.decide(request.approval_id, subject_id="alice", project_id="p1", decision=decision, decision_by="alice", reason="human decision", payload={"instruction": "safe alternative"})
            assert result.state is decision
        store.close()


def test_secret_like_fields_and_oversized_values_fail_closed() -> None:
    store = HumanApprovalService()
    with pytest.raises(ValueError, match="secret-like"):
        store.create({"subject_id": "alice", "project_id": "p1", "kind": "input", "gate": "human_input", "action": "ask", "summary": "input", "requested_by": "alice", "metadata": {"api_key": "do-not-store"}})
    with pytest.raises(ValueError, match="safety limit"):
        store.create({"subject_id": "alice", "project_id": "p1", "kind": "input", "gate": "human_input", "action": "ask", "summary": "input", "requested_by": "alice", "metadata": {"text": "x" * (256 * 1024)}})
    store.close()


def test_expiry_is_fail_closed_and_restart_safe() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "approvals.sqlite3"
        store = HumanApprovalService(path)
        request = store.create({"subject_id": "alice", "project_id": "p1", "kind": "approval", "gate": "security", "action": "sensitive", "summary": "security gate", "requested_by": "alice", "expires_in": 0.01})
        time.sleep(0.03)
        assert store.get(request.approval_id, subject_id="alice", project_id="p1").state is ApprovalState.EXPIRED
        store.close()
        reopened = HumanApprovalService(path)
        assert reopened.get(request.approval_id, subject_id="alice", project_id="p1").state is ApprovalState.EXPIRED
        reopened.close()


def test_stale_revision_and_cross_project_are_rejected() -> None:
    store = HumanApprovalService()
    request = store.create({"subject_id": "alice", "project_id": "p1", "kind": "approval", "gate": "cost", "action": "buy", "summary": "cost gate", "requested_by": "alice"})
    with pytest.raises(PermissionError):
        store.decide(request.approval_id, subject_id="alice", project_id="p2", decision=ApprovalState.APPROVED, decision_by="alice", reason="no")
    with pytest.raises(ValueError, match="revision conflict"):
        store.decide(request.approval_id, subject_id="alice", project_id="p1", decision=ApprovalState.APPROVED, decision_by="alice", reason="yes", expected_revision=9)
    store.close()


def test_control_api_exposes_queue_decision_and_events() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        service = ControlApiService(root)
        server = create_server(service, host="127.0.0.1", port=0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        host, port = server.server_address
        connection = HTTPConnection(host, port, timeout=3)
        body = json.dumps({"subject_id": "alice", "project_id": "p1", "kind": "approval", "gate": "destructive", "action": "delete", "summary": "delete data", "requested_by": "alice"})
        connection.request("POST", "/api/v1/approvals", body, {"Content-Type": "application/json"})
        response = connection.getresponse()
        assert response.status == 201
        approval = json.loads(response.read())
        approval_id = approval["approval_id"]
        connection.request("GET", "/api/v1/approvals", headers={"X-SI-Subject": "alice", "X-SI-Project": "p1"})
        response = connection.getresponse()
        assert response.status == 200
        assert json.loads(response.read())[0]["approval_id"] == approval_id
        connection.request("POST", f"/api/v1/approvals/{approval_id}/decide", json.dumps({"subject_id": "alice", "project_id": "p1", "decision": "rejected", "decision_by": "alice", "reason": "not approved"}), {"Content-Type": "application/json"})
        response = connection.getresponse()
        assert response.status == 200
        assert json.loads(response.read())["state"] == "rejected"
        connection.request("GET", f"/api/v1/approvals/{approval_id}/events", headers={"X-SI-Subject": "alice", "X-SI-Project": "p1"})
        response = connection.getresponse()
        assert response.status == 200
        assert len(json.loads(response.read())) == 2
        connection.close()
        server.shutdown()
        server.server_close()
