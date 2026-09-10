"""Phase 40 evidence, provenance, timeline, persistence, and API regression tests."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.request import Request, urlopen

from core.control_api.server import create_server
from core.control_api.service import ControlApiService
from core.evidence.models import EvidenceKind, EvidenceRecord, VerificationState
from core.evidence.service import EvidenceService
from core.evidence.store import EvidenceStore


def test_evidence_record_rejects_invalid_confidence() -> None:
    try:
        EvidenceRecord.new(claim="x", kind=EvidenceKind.FACT, source="test", confidence=1.1)
    except ValueError as exc:
        assert "between 0 and 1" in str(exc)
    else:
        raise AssertionError("invalid confidence was accepted")


def test_store_persists_timestamps_and_marks_superseded() -> None:
    with TemporaryDirectory() as directory:
        path = Path(directory) / "evidence.json"
        store = EvidenceStore(path)
        first = EvidenceRecord.new(claim="first", kind=EvidenceKind.OBSERVATION, source="sensor", confidence=0.7)
        store.record(first)
        second = EvidenceRecord.new(
            claim="updated", kind=EvidenceKind.FACT, source="verification", confidence=0.95,
            verification=VerificationState.VERIFIED, supersedes=first.id,
        )
        store.record(second)
        restored = EvidenceStore(path)
        assert restored.get(first.id).verification is VerificationState.SUPERSEDED
        assert restored.get(first.id).created_at == first.created_at
        assert restored.get(second.id).verification is VerificationState.VERIFIED


def test_service_distinguishes_kinds_and_builds_run_timeline() -> None:
    with TemporaryDirectory() as directory:
        service = EvidenceService(str(Path(directory) / "evidence.json"))
        service.record({"claim": "observed", "kind": "observation", "source": "test", "confidence": 0.8, "run_id": "run_1"})
        service.record({"claim": "likely", "kind": "inference", "source": "test", "confidence": 0.4, "run_id": "run_1"})
        service.record({"claim": "unknown", "kind": "uncertainty", "source": "test", "confidence": 0.1, "run_id": "run_1"})
        timeline = service.timeline("run_1")
        assert timeline["counts"] == {
            "total": 3, "facts": 0, "observations": 1, "inferences": 1, "uncertainties": 1,
            "verified": 0, "contradicted": 0, "superseded": 0,
        }
        assert all(item["run_id"] == "run_1" for item in timeline["events"])


def test_control_api_exposes_evidence_records_and_timeline() -> None:
    with TemporaryDirectory() as directory:
        root = Path(directory)
        server = create_server(ControlApiService(root), host="127.0.0.1", port=0)
        server.server_activate()
        server.server_bind()
        # The test server is intentionally driven through the public HTTP boundary.
        import threading

        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            base = f"http://127.0.0.1:{server.server_port}"
            body = json.dumps({
                "claim": "run accepted", "kind": "fact", "source": "control-api", "confidence": 1.0, "run_id": "run-test"
            }).encode()
            request = Request(f"{base}/api/v1/evidence", data=body, method="POST", headers={"Content-Type": "application/json"})
            with urlopen(request, timeout=3) as response:
                assert response.status == 201
                evidence = json.load(response)
            with urlopen(f"{base}/api/v1/evidence/records", timeout=3) as response:
                records = json.load(response)
            assert records[0]["id"] == evidence["id"]
            with urlopen(f"{base}/api/v1/runs/run-test/timeline", timeout=3) as response:
                timeline = json.load(response)
            assert timeline["counts"]["facts"] == 1
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)
