"""Small OpenAPI description for the stable SI Control API surface."""

OPENAPI_VERSION = "3.1.0"


def document() -> dict[str, object]:
    return {
        "openapi": OPENAPI_VERSION,
        "info": {"title": "SI-Agents Control API", "version": "1.0", "description": "Machine-facing control and inspection boundary for SI-Agents."},
        "paths": {
            "/api/v1": {"get": {"responses": {"200": {"description": "Control API snapshot"}}}},
            "/api/v1/health": {"get": {"responses": {"200": {"description": "Healthy API process"}}}},
            "/api/v1/agents": {"get": {"responses": {"200": {"description": "Canonical agent catalog"}}}},
            "/api/v1/teams": {"get": {"responses": {"200": {"description": "Team catalog"}}}},
            "/api/v1/workflows": {"get": {"responses": {"200": {"description": "Organization workflows"}}}},
            "/api/v1/organization": {"get": {"responses": {"200": {"description": "Organization expansion"}}}},
            "/api/v1/skills": {"get": {"responses": {"200": {"description": "Portable Skill inventory"}}}},
            "/api/v1/memory": {"get": {"responses": {"200": {"description": "Memory read model"}}}},
            "/api/v1/governance": {"get": {"responses": {"200": {"description": "Governance read model"}}}},
            "/api/v1/evidence": {"get": {"responses": {"200": {"description": "Control-plane evidence summary"}}, "post": {"responses": {"201": {"description": "Evidence record"}, "400": {"description": "Invalid evidence"}}}},
            "/api/v1/evidence/records": {"get": {"responses": {"200": {"description": "Evidence records ordered by creation time"}}}},
            "/api/v1/evidence/{evidence_id}": {"get": {"parameters": [{"name": "evidence_id", "in": "path", "required": True, "schema": {"type": "string"}}], "responses": {"200": {"description": "Evidence record"}, "404": {"description": "Evidence not found"}}}},
            "/api/v1/evidence/{evidence_id}/verify": {"post": {"parameters": [{"name": "evidence_id", "in": "path", "required": True, "schema": {"type": "string"}}], "responses": {"200": {"description": "Updated verification state"}, "400": {"description": "Invalid verification state"}}}},
            "/api/v1/runs/{run_id}/timeline": {"get": {"parameters": [{"name": "run_id", "in": "path", "required": True, "schema": {"type": "string"}}], "responses": {"200": {"description": "Evidence timeline for a run"}}}},
            "/api/v1/environments": {"get": {"responses": {"200": {"description": "Sanitized runtime context"}}}},
            "/api/v1/harnesses": {"get": {"responses": {"200": {"description": "Registered adapter families"}}}},
            "/api/v1/deployments": {"get": {"responses": {"200": {"description": "Registered harness targets and deployment plans"}}}, "post": {"responses": {"201": {"description": "Deployment plan created"}, "400": {"description": "Invalid deployment plan"}}}},
            "/api/v1/settings": {"get": {"responses": {"200": {"description": "Effective control-center settings"}}}},
            "/api/v1/visualization": {"get": {"responses": {"200": {"description": "Deterministic organization/workflow graph read model"}}}},
            "/api/v1/control-center": {"get": {"responses": {"200": {"description": "Control Center aggregate read model"}}}},
            "/api/v1/agent-builder": {"get": {"responses": {"200": {"description": "Persisted user-authored agent drafts"}}}},
            "/api/v1/agent-builder/from/{agent_id}": {"get": {"parameters": [{"name": "agent_id", "in": "path", "required": True, "schema": {"type": "string"}}], "responses": {"200": {"description": "Editable projection of a canonical agent"}, "404": {"description": "Agent not found"}}}},
            "/api/v1/agent-builder/drafts/{draft_id}": {"get": {"parameters": [{"name": "draft_id", "in": "path", "required": True, "schema": {"type": "string"}}], "responses": {"200": {"description": "Agent draft"}, "404": {"description": "Draft not found"}}}},
            "/api/v1/agent-builder/validate": {"post": {"responses": {"200": {"description": "Validation and deterministic Markdown preview"}, "400": {"description": "Invalid request"}}}},
            "/api/v1/agent-builder/drafts": {"post": {"responses": {"201": {"description": "Validated draft saved"}, "400": {"description": "Invalid draft"}}}},
            "/api/v1/agent-builder/drafts/{draft_id}/test": {"post": {"parameters": [{"name": "draft_id", "in": "path", "required": True, "schema": {"type": "string"}}], "responses": {"200": {"description": "Non-executing validation test"}, "404": {"description": "Draft not found"}}}},
            "/api/v1/agent-builder/drafts/{draft_id}/archive": {"post": {"parameters": [{"name": "draft_id", "in": "path", "required": True, "schema": {"type": "string"}}], "responses": {"200": {"description": "Draft archived"}, "404": {"description": "Draft not found"}}}},
            "/api/v1/events": {"get": {"responses": {"200": {"description": "API events"}}}},
            "/api/v1/runs": {"get": {"responses": {"200": {"description": "Run records"}}}, "post": {"responses": {"202": {"description": "Governed run accepted"}, "400": {"description": "Invalid request"}, "403": {"description": "Governance denied"}}}},
            "/api/v1/runs/{run_id}": {"get": {"parameters": [{"name": "run_id", "in": "path", "required": True, "schema": {"type": "string"}}], "responses": {"200": {"description": "Run record"}, "404": {"description": "Run not found"}}}},
        },
    }
