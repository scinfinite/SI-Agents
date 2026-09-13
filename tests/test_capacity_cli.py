from __future__ import annotations

from core.cli.capacity import main


def test_capacity_cli_json_reports_termux_high_denial(capsys) -> None:
    code = main(["--target", "termux", "--action", "compile", "--json"])
    output = capsys.readouterr().out
    assert code == 3
    assert '"allowed": false' in output
    assert '"level": "high"' in output


def test_capacity_cli_allows_termux_low(capsys) -> None:
    code = main(["--target", "termux", "--level", "low", "--action", "status"])
    output = capsys.readouterr().out
    assert code == 0
    assert "allowed: yes" in output
    assert "workers: 1" in output
