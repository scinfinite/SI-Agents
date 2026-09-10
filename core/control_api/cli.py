"""Command-line launcher for the localhost Control API."""

from __future__ import annotations

import argparse
from pathlib import Path

from .server import create_server
from .service import ControlApiService


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="si-api", description="Run the SI-Agents localhost Control API")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    service = ControlApiService(args.root)
    server = create_server(service, args.host, args.port)
    print(f"SI-Agents Control API listening on http://{args.host}:{args.port}/api/v1")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
