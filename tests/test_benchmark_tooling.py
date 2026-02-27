"""Tests for benchmark tooling robustness and signaling behavior."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPARE = ROOT / "benchmarks" / "compare.py"
BENCH_IMPORT = ROOT / "benchmarks" / "bench_import.py"
BENCH_VALIDATE = ROOT / "benchmarks" / "bench_validate.py"
BENCH_ENV = ROOT / "benchmarks" / "bench_env.py"


def _run(*args):
    return subprocess.run(
        [sys.executable, *map(str, args)],
        capture_output=True,
        text=True,
    )


def test_compare_requires_required_args():
    result = _run(COMPARE, "--baseline", "foo.json")
    assert result.returncode == 2
    assert "Usage: compare.py" in result.stderr


def test_compare_fails_when_baseline_missing(tmp_path):
    current_dir = tmp_path / "current"
    current_dir.mkdir()

    result = _run(
        COMPARE,
        "--baseline",
        tmp_path / "missing.json",
        "--current",
        current_dir,
    )
    assert result.returncode == 2
    assert "baseline file not found" in result.stderr


def test_compare_reports_missing_baseline_metrics_as_incomplete(tmp_path):
    baseline = tmp_path / "baseline.json"
    baseline.write_text(json.dumps({"import": {"median_ms": 0.2}}))

    current_dir = tmp_path / "out"
    current_dir.mkdir()
    (current_dir / "import.json").write_text(json.dumps({"median_ms": 0.21, "result": "PASS"}))
    (current_dir / "validate.json").write_text(json.dumps({"median_ms": 0.01, "result": "PASS"}))
    (current_dir / "env.json").write_text(json.dumps({"overhead_ms": 0.001, "result": "PASS"}))

    result = _run(
        COMPARE,
        "--baseline",
        baseline,
        "--current",
        current_dir,
    )
    assert result.returncode == 0
    assert "baseline entry missing" in result.stdout
    assert "Comparison incomplete" in result.stdout


def test_benchmark_scripts_require_json_path():
    for script in (BENCH_IMPORT, BENCH_VALIDATE, BENCH_ENV):
        result = _run(script, "--json")
        assert result.returncode == 2
        assert "requires an output path" in result.stderr


def test_bench_import_creates_json_parent_dir(tmp_path):
    output = tmp_path / "nested" / "bench" / "import.json"
    result = _run(BENCH_IMPORT, "--json", output)

    assert result.returncode == 0
    assert output.exists()
    payload = json.loads(output.read_text())
    assert payload["benchmark"] == "import"
    assert payload["result"] in ("PASS", "FAIL")
    assert "runtime" in payload
    assert "target" in payload
