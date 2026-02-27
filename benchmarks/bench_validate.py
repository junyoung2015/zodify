"""Benchmark: validate() speed (median < 1ms)."""

import json
import os
import platform
import sys
import time
import statistics

WARMUP = 5
MEASURED = 30
ITERATIONS = 1000
THRESHOLD_SEC = 0.001


def usage():
    return "Usage: bench_validate.py [--json <output-path>]"


def parse_json_arg(argv):
    json_path = None
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
        raise ValueError(f"Unknown argument: {arg}")
    return json_path


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


def main():
    from zodify import validate

    try:
        json_path = parse_json_arg(sys.argv[1:])
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        print(usage(), file=sys.stderr)
        return 2

    # Fixture: 10 keys, 2 levels nesting, one list field
    schema = {
        "name": str,
        "age": int,
        "email": str,
        "active": bool,
        "score": float,
        "tags": [str],
        "address": {
            "street": str,
            "city": str,
            "zip": str,
        },
        "role": str,
        "level": int,
        "verified": bool,
    }

    data = {
        "name": "Alice",
        "age": 30,
        "email": "alice@example.com",
        "active": True,
        "score": 95.5,
        "tags": ["admin", "user"],
        "address": {
            "street": "123 Main St",
            "city": "Springfield",
            "zip": "62701",
        },
        "role": "engineer",
        "level": 5,
        "verified": True,
    }

    print("Benchmarking: validate() with 10-key/2-level schema")
    print(f"Runtime: {runtime_label()}")
    print("Target: ubuntu-latest x64, CPython 3.12")
    print(f"Protocol: {WARMUP} warmup + {MEASURED} measured runs")
    print()

    # Warmup
    for _ in range(WARMUP):
        for _ in range(ITERATIONS):
            validate(schema, data)

    # Measured runs (batched, then normalized to per-call time)
    times = []
    for _ in range(MEASURED):
        start = time.perf_counter()
        for _ in range(ITERATIONS):
            validate(schema, data)
        elapsed = time.perf_counter() - start
        times.append(elapsed / ITERATIONS)

    med = statistics.median(times)
    result = "PASS" if med < THRESHOLD_SEC else "FAIL"
    print(f"  Median: {med * 1000:.4f} ms")
    print(f"  Min:    {min(times) * 1000:.4f} ms")
    print(f"  Max:    {max(times) * 1000:.4f} ms")
    print(f"  Threshold: {THRESHOLD_SEC * 1000:.3f} ms")
    print(f"  Result: {result}")

    if json_path:
        out = {
            "benchmark": "validate",
            "runtime": runtime_label(),
            "target": "ubuntu-latest x64, CPython 3.12",
            "median_ms": med * 1000,
            "min_ms": min(times) * 1000,
            "max_ms": max(times) * 1000,
            "threshold_ms": THRESHOLD_SEC * 1000,
            "result": result,
        }
        write_json(json_path, out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
