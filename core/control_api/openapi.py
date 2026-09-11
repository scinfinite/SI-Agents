"""Small OpenAPI description for the stable SI Control API surface."""

OPENAPI_VERSION = "3.1.0"


def _get(description: str) -> dict[str, object]:
    return {"get": {"responses": {"200": {"description": description}}}}


def _post(description: str) -> dict[str, object]:
    return {"post": {"responses": {"201": {"description": description}, "400": {"description": "Invalid request"}}}}


def document() -> dict[str, object]:
    descriptions = {
        "/api/v1": "Control API snapshot", "/api/v1/health": "Healthy API process", "/api/v1/agents": "Canonical agent catalog",
        "/api/v1/teams": "Team catalog", "/api/v1/workflows": "Organization workflows", "/api/v1/organization": "Organization expansion",
        "/api/v1/skills": "Portable Skill inventory", "/api/v1/memory": "Memory read model", "/api/v1/governance": "Governance read model",
        "/api/v1/evidence/records": "Evidence records", "/api/v1/environments": "Sanitized runtime context",
        "/api/v1/harnesses": "Registered adapter families", "/api/v1/deployments": "Harness targets and deployment plans",
        "/api/v1/settings": "Effective control-center settings", "/api/v1/visualization": "Organization/workflow graph",
        "/api/v1/control-center": "Control Center aggregate", "/api/v1/agent-builder": "Agent drafts", "/api/v1/events": "API events",
        "/api/v1/runs": "Run records",
    }
    paths: dict[str, object] = {path: _get(description) for path, description in descriptions.items()}
    paths["/api/v1/evidence"] = {**_get("Control-plane evidence summary"), **_post("Evidence record")}
    paths["/api/v1/deployments"] = {**_get("Harness targets and deployment plans"), **_post("Deployment plan created")}
    paths["/api/v1/runs"] = {**_get("Run records"), "post": {"responses": {"202": {"description": "Governed run accepted"}, "400": {"description": "Invalid request"}, "403": {"description": "Governance denied"}}}}
    paths["/api/v1/evidence/{evidence_id}"] = _get("Evidence record")
    paths["/api/v1/evidence/{evidence_id}/verify"] = {"post": {"responses": {"200": {"description": "Updated verification state"}, "400": {"description": "Invalid verification state"}}}}
    paths["/api/v1/runs/{run_id}"] = _get("Run record")
    paths["/api/v1/runs/{run_id}/timeline"] = _get("Evidence timeline for a run")
    paths["/api/v1/agent-builder/from/{agent_id}"] = _get("Editable canonical-agent projection")
    paths["/api/v1/agent-builder/drafts/{draft_id}"] = _get("Agent draft")
    paths["/api/v1/agent-builder/validate"] = _post("Validation result")
    paths["/api/v1/agent-builder/drafts"] = _post("Validated draft saved")
    paths["/api/v1/agent-builder/drafts/{draft_id}/test"] = _post("Non-executing draft test")
    paths["/api/v1/agent-builder/drafts/{draft_id}/archive"] = _post("Draft archived")
    return {"openapi": OPENAPI_VERSION, "info": {"title": "SI-Agents Control API", "version": "1.0"}, "paths": paths}
