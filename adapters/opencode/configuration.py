"""Generate safe OpenCode project configuration without embedding secrets."""

import json
from typing import Mapping


def render_opencode_config(
    models: Mapping[str, str],
    *,
    base_url: str,
    provider_id: str = "si-agents",
) -> str:
    """Return deterministic OpenCode JSON for an OpenAI-compatible provider.

    This config is intentionally provider configuration, not an authorization
    mechanism. Credentials should be supplied through OpenCode's auth/env flow.
    """
    if not provider_id.strip() or not base_url.strip():
        raise ValueError("provider_id and base_url are required")
    if not models:
        raise ValueError("at least one model is required")
    model_config = {
        model_id: {"name": name, "modelID": model_id}
        for model_id, name in sorted(models.items())
        if model_id.strip() and name.strip()
    }
    if len(model_config) != len(models):
        raise ValueError("model ids and names must not be empty")
    payload = {
        "$schema": "https://opencode.ai/config.json",
        "providers": {
            provider_id: {
                "name": "SI-Agents",
                "package": "@opencode/ai/providers/openai-compatible",
                "settings": {"baseURL": base_url.rstrip("/") + "/v1"},
                "models": model_config,
            }
        },
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"
