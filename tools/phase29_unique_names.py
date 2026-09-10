from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIVISION_LABELS = {
    "engineering": "Engineering", "debugging": "Debugging", "verification": "Verification",
    "architecture": "Architecture", "security": "Security", "research": "Research", "operations": "Operations",
}

def main() -> int:
    agents = ROOT / "agents"
    names = {}
    for path in sorted(p for p in agents.rglob("*.md") if p.name != "README.md"):
        lines = path.read_text(encoding="utf-8").splitlines()
        data = {line.split(":", 1)[0]: line.split(":", 1)[1].strip() for line in lines[1:7] if ":" in line}
        name = f"{DIVISION_LABELS[data['division']]} {data['name']}"
        lines[lines.index(next(line for line in lines if line.startswith("name: ")))] = f"name: {name}"
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        names[data["id"]] = name
    catalog_path = ROOT / "config/agent-catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    for agent in catalog["agents"]:
        agent["name"] = names[agent["id"]]
    catalog_path.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    subprocess.run(["git", "config", "user.name", "github-actions[bot]"], cwd=ROOT, check=True)
    subprocess.run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"], cwd=ROOT, check=True)
    subprocess.run(["git", "add", "agents", "config/agent-catalog.json"], cwd=ROOT, check=True)
    subprocess.run(["git", "commit", "-m", "fix(phase29): make persona identities globally unique"], cwd=ROOT, check=True)
    subprocess.run(["git", "push"], cwd=ROOT, check=True)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
