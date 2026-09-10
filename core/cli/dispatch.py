"""Dispatch the stable ``si`` command to legacy commands or the Web surface."""

from __future__ import annotations

import sys

from core.web.cli import main as web_main


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments and arguments[0] == "web":
        return web_main(arguments[1:])
    from core.cli.main import main as legacy_main

    return legacy_main(arguments)


if __name__ == "__main__":
    raise SystemExit(main())
