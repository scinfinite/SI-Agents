"""CLI entry point for the SI terminal operator control center."""
from __future__ import annotations

import argparse
from pathlib import Path

from core.control_api.service import ControlApiService

from .app import VIEWS, TuiApp, terminal_colors_disabled


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="si tui", description="SI-Agents advanced terminal operator control center")
    parser.add_argument("--root", default=".", help="SI-Agents repository root")
    parser.add_argument("--view", choices=VIEWS, default="overview")
    parser.add_argument("--filter", dest="filter_text", default="")
    parser.add_argument("--once", action="store_true", help="render once and exit")
    parser.add_argument("--command", action="append", default=[], help="execute a command before rendering; repeatable")
    parser.add_argument("--no-color", action="store_true", help="disable terminal control sequences")
    parser.add_argument("--page-size", type=int, default=20, help="maximum list rows rendered (1-100)")
    parser.add_argument("--refresh", type=float, default=0.0, help="bounded refresh interval in seconds (0-60)")
    parser.add_argument("--approval-subject", default="", help="identity subject used by the approvals view")
    parser.add_argument("--approval-project", default="", help="project boundary used by the approvals view")
    args = parser.parse_args(argv)

    app = TuiApp(
        ControlApiService(Path(args.root)),
        color=not (args.no_color or terminal_colors_disabled()),
        page_size=args.page_size,
    )
    app.state = app.state.__class__(args.view, args.filter_text, 0)
    app.approval_subject = args.approval_subject
    app.approval_project = args.approval_project
    for command in args.command:
        if not app.handle(command):
            return 0
    if args.once:
        print(app.render())
        return 0
    return app.run(refresh_seconds=args.refresh)


if __name__ == "__main__":
    raise SystemExit(main())
