"""Small OpenAPI description for the stable SI Control API surface."""

from __future__ import annotations


OPENAPI_VERSION = "3.1.0"


def document() -> dict[str, object]:
    return {
        "openapi": OPENAPI_VERSION,
        "info": {"title": "SI-Agents Control API", "version": "1.0", "description": "Machine-facing control and inspection boundary for SI-Agents."},
        "paths": {
            "/api/v1/health": {"get": {"responses": {"200": {"description": "Healthy API process"}}}},
            "/api/v1/agents": {"get": {"responses": {"200": {"description": "Canonical agent catalog"}}}},
            "/api/v1/teams": {"get": {"responses": {"200": {"description": "Team catalog"}}}},
            "/api/v1/workflows": {"get": {"responses": {"200": {"description": "Organization workflows"}}}},
            "/api/v1/organization": {"get": {"responses": {"200": {"description": "Organization expansion"}}}},
            "/api/v1/skills": {"get": {"responses": {"200": {"description": "Portable Skill inventory"}}}},
            "/api/v1/memory": {"get": {"responses": {"200": {"description": "Memory read model"}}}},
            "/api/v1/governance": {"get": {"responses": {"200": {"description": "Governance read model"}}}},
            "/api/v1/events": {"get": {"responses": {"200": {"description": "API events"}}}},
            "/api/v1/runs": {
                "get": {"responses": {"200": {"description": "Run records"}}},
                "post": {"responses": {"202": {"description": "Governed run accepted"}, "400": {"description": "Invalid request"}, "403": {"description": "Governance denied"}}},
            },
            "/api/v1/runs/{run_id}": {"get": {"parameters": [{"name": "run_id", "in": "path", "required": True, "schema": {"type": "string"}}], "responses": {"200": {"description": "Run record"}, "404": {"description": "Run not found"}}}},
        },
    }
