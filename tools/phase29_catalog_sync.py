"""Synchronize the typed agent catalog with the generated persona corpus."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

DIVISIONS = [
    {"id": "engineering", "name": "Engineering", "description": "Build and maintain software systems."},
    {"id": "debugging", "name": "Debugging", "description": "Reproduce failures and isolate root causes."},
    {"id": "verification", "name": "Verification", "description": "Test, review, and challenge engineering claims."},
    {"id": "architecture", "name": "Architecture", "description": "Design system boundaries and technical decisions."},
    {"id": "security", "name": "Security", "description": "Identify and govern security risks and controls."},
    {"id": "research", "name": "Research", "description": "Investigate technologies, evidence, and external systems."},
    {"id": "operations", "name": "Operations", "description": "Release, reliability, cost, and operational readiness."},
]


def fields(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines()[1:7]:
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return result


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    index = json.loads((root / "config/persona-source-index.json").read_text(encoding="utf-8"))
    agents = []
    for item in index["agents"]:
        data = fields(root / item["path"])
        agents.append({
            "id": data["id"], "name": data["name"], "division": data["division"],
            "description": data["description"],
            "responsibilities": ["apply role expertise", "produce scoped work", "preserve evidence"],
            "deliverables": ["role-specific work product", "verification evidence"],
            "success_criteria": ["scope is respected", "claims are evidence-backed"],
            "boundaries": ["does not self-authorize privileges", "does not bypass governance", "does not expose secrets"],
            "skills": ["inspect-repository", "verify-change"],
            "capabilities": ["filesystem", "code_search"],
            "permissions": ["repository_read"],
            "harnesses": ["opencode", "codex", "claude-code", "cline", "antigravity"],
            "environments": ["terminal", "termux", "codespace"],
            "status": "cataloged",
        })
    if len(agents) != 279 or len({a["id"] for a in agents}) != 279:
        raise SystemExit("catalog parity failure")
    catalog = {"version": 1, "schema": "si-agents.agent-catalog.v1", "divisions": DIVISIONS, "agents": agents}
    (root / "config/agent-catalog.json").write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    subprocess.run(["git", "add", "config/agent-catalog.json"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-m", "feat(phase29): sync typed agent catalog"], cwd=root, check=True)
    subprocess.run(["git", "push"], cwd=root, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
