from pathlib import Path
import subprocess
import sys


FIXTURE = Path(__file__).parents[1] / "fixtures" / "broken_project"
CASE = FIXTURE / "acceptance_case.py"


def test_broken_fixture_reproduces_expected_failure() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", str(CASE), "-q"],
        cwd=FIXTURE,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "assert 5" not in completed.stdout
    assert "failed" in (completed.stdout + completed.stderr).lower()
