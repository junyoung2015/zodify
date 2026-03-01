"""Benchmark: zodify import time (median target < 5ms)."""

import json
import os
import platform
import subprocess
import sys
import statistics

WARMUP = 5
MEASURED = 30
TIMEOUT_SEC = 10
THRESHOLD_SEC = 0.005


def usage():
    return (
        "Usage: bench_import.py [--json <output-path>] "
        "[--enforce-threshold]"
    )


def parse_json_arg(argv):
    json_path = None
    enforce_threshold = False
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--json":
            if json_path is not None:
                raise ValueError("--json provided more than once")
            if i + 1 >= len(argv) or argv[i + 1].startswith("--"):
                raise ValueError("--json requires an output path")
            json_path = argv[i + 1]
            i += 2
            continue
        if arg == "--enforce-threshold":
            enforce_threshold = True
            i += 1
            continue
        raise ValueError(f"Unknown argument: {arg}")
    return json_path, enforce_threshold


def runtime_label():
    return (
        f"{platform.system()} {platform.machine()}, "
        f"CPython {sys.version_info.major}.{sys.version_info.minor}."
        f"{sys.version_info.micro}"
    )


def write_json(path, payload):
    output_dir = os.path.dirname(os.path.abspath(path))
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)


def measure_import():
    """Measure import time in a fresh subprocess."""
    try:
        result = subprocess.run(
            [sys.executable, "-c",
             "import time; s=time.perf_counter(); import zodify; "
             "print(time.perf_counter()-s)"],
            capture_output=True, text=True, check=True,
            timeout=TIMEOUT_SEC,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("import benchmark subprocess timed out") from exc
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        raise RuntimeError(f"import benchmark subprocess failed: {stderr}") from exc
    return float(result.stdout.strip())


def main():
    try:
        json_path, enforce_threshold = parse_json_arg(sys.argv[1:])
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        print(usage(), file=sys.stderr)
        return 2

    print("Benchmarking: import zodify")
    print(f"Runtime: {runtime_label()}")
    print("Target: ubuntu-latest x64, CPython 3.12")
    print(f"Protocol: {WARMUP} warmup + {MEASURED} measured runs")
    print()

    # Warmup
    for _ in range(WARMUP):
        measure_import()

    # Measured runs
    times = [measure_import() for _ in range(MEASURED)]

    med = statistics.median(times)
    result = "PASS" if med < THRESHOLD_SEC else "FAIL"
    print(f"  Median: {med * 1000:.3f} ms")
    print(f"  Min:    {min(times) * 1000:.3f} ms")
    print(f"  Max:    {max(times) * 1000:.3f} ms")
    print(f"  Threshold: {THRESHOLD_SEC * 1000:.3f} ms")
    print(f"  Result: {result} (informational unless --enforce-threshold)")

    if json_path:
        data = {
            "benchmark": "import",
            "runtime": runtime_label(),
            "target": "ubuntu-latest x64, CPython 3.12",
            "median_ms": med * 1000,
            "min_ms": min(times) * 1000,
            "max_ms": max(times) * 1000,
            "threshold_ms": THRESHOLD_SEC * 1000,
            "result": result,
        }
        write_json(json_path, data)
    if enforce_threshold and result == "FAIL":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
