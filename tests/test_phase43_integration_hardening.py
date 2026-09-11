import json

from core.hardening.integration import IntegrationAuditor


def test_integration_audit_fails_closed_on_non_object_agent_catalog(tmp_path):
    root = tmp_path
    (root / "config").mkdir()
    (root / "config/agent-catalog.json").write_text(json.dumps([]), encoding="utf-8")

    report = IntegrationAuditor(root).run()

    assert report.ready is False
    check = next(item for item in report.checks if item.name == "agent_catalog")
    assert check.passed is False
    assert "catalog root must be an object" in check.detail
