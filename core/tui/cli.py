"""CLI entry point for the SI terminal operator interface."""

from __future__ import annotations

import argparse
from pathlib import Path

from core.control_api.service import ControlApiService

from .app import TuiApp, terminal_colors_disabled


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="si tui", description="SI-Agents terminal operator interface")
    parser.add_argument("--root", default=".", help="SI-Agents repository root")
    parser.add_argument("--view", choices=__import__("core.tui.app", fromlist=["VIEWS"]).VIEWS, default="overview")
    parser.add_argument("--filter", dest="filter_text", default="")
    parser.add_argument("--once", action="store_true", help="render once and exit")
    parser.add_argument("--no-color", action="store_true", help="disable terminal color/control sequences")
    args = parser.parse_args(argv)
    app = TuiApp(ControlApiService(Path(args.root)), color=not (args.no_color or terminal_colors_disabled()))
    app.handle(f"/{args.filter_text}") if args.filter_text else None
    app.handle(str(__import__("core.tui.app", fromlist=["VIEWS"]).VIEWS.index(args.view) + 1))
    return app.run() if not args.once else (print(app.render()) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
