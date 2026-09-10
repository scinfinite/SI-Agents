#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON_BIN="${PYTHON_BIN:-python3}"

"$PYTHON_BIN" -m pip install -r requirements-dev.txt
"$PYTHON_BIN" -m build
"$PYTHON_BIN" -m ruff check .
"$PYTHON_BIN" -m compileall -q adapters agents core skills tools
"$PYTHON_BIN" -m pytest --strict-config --strict-markers
"$PYTHON_BIN" -m core.cli.main audit --json

echo "SI verification: PASS"
