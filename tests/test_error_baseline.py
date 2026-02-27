"""Tests for the error baseline script."""

import subprocess
import sys
from pathlib import Path

SCRIPT = str(Path(__file__).resolve().parent.parent / "scripts" / "error_baseline.py")
BASELINE = Path(__file__).resolve().parent.parent / "scripts" / "baseline_final.txt"


def test_error_baseline_script_runs_successfully():
    result = subprocess.run(
        [sys.executable, SCRIPT],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert result.stderr == ""
    lines = result.stdout.strip().split("\n")
    # Must produce at least 30 error lines
    assert len(lines) >= 30


def test_error_baseline_script_output_is_deterministic():
    r1 = subprocess.run(
        [sys.executable, SCRIPT],
        capture_output=True, text=True,
    )
    r2 = subprocess.run(
        [sys.executable, SCRIPT],
        capture_output=True, text=True,
    )
    assert r1.stdout == r2.stdout


def test_error_baseline_script_matches_checked_in_baseline():
    result = subprocess.run(
        [sys.executable, SCRIPT],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout == BASELINE.read_text()
