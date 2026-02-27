"""Benchmark: env() overhead vs os.environ.get() (overhead < 0.1ms)."""

import json
import os
import platform
import sys
import time
import statistics

WARMUP = 5
MEASURED = 30
ITERATIONS = 1000
THRESHOLD_SEC = 0.0001


def usage():
    return "Usage: bench_env.py [--json <output-path>]"


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
    from zodify import env

    try:
        json_path = parse_json_arg(sys.argv[1:])
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        print(usage(), file=sys.stderr)
        return 2

    os.environ["ZODIFY_BENCH_VAR"] = "42"
    try:
        print("Benchmarking: env() per-call overhead vs os.environ.get()")
        print(f"Runtime: {runtime_label()}")
        print("Target: ubuntu-latest x64, CPython 3.12")
        print(f"Protocol: {WARMUP} warmup + {MEASURED} measured runs "
              f"({ITERATIONS} calls each)")
        print()

        # Warmup
        for _ in range(WARMUP):
            for _ in range(ITERATIONS):
                env("ZODIFY_BENCH_VAR", int)
            for _ in range(ITERATIONS):
                os.environ.get("ZODIFY_BENCH_VAR")

        # Measure env()
        env_times = []
        for _ in range(MEASURED):
            start = time.perf_counter()
            for _ in range(ITERATIONS):
                env("ZODIFY_BENCH_VAR", int)
            elapsed = time.perf_counter() - start
            env_times.append(elapsed / ITERATIONS)

        # Measure os.environ.get()
        raw_times = []
        for _ in range(MEASURED):
            start = time.perf_counter()
            for _ in range(ITERATIONS):
                os.environ.get("ZODIFY_BENCH_VAR")
            elapsed = time.perf_counter() - start
            raw_times.append(elapsed / ITERATIONS)

        env_med = statistics.median(env_times)
        raw_med = statistics.median(raw_times)
        signed_delta = env_med - raw_med
        overhead = max(0.0, signed_delta)

        result = "PASS" if overhead < THRESHOLD_SEC else "FAIL"
        print(f"  env() median:            {env_med * 1000:.4f} ms/call")
        print(f"  os.environ.get() median: {raw_med * 1000:.4f} ms/call")
        print(f"  Signed delta:            {signed_delta * 1000:.4f} ms/call")
        print(f"  Overhead (normalized):   {overhead * 1000:.4f} ms/call")
        print(f"  Threshold:          {THRESHOLD_SEC * 1000:.4f} ms/call")
        print(f"  Result: {result}")

        if json_path:
            out = {
                "benchmark": "env",
                "runtime": runtime_label(),
                "target": "ubuntu-latest x64, CPython 3.12",
                "env_median_ms": env_med * 1000,
                "raw_median_ms": raw_med * 1000,
                "signed_delta_ms": signed_delta * 1000,
                "overhead_ms": overhead * 1000,
                "threshold_ms": THRESHOLD_SEC * 1000,
                "result": result,
            }
            write_json(json_path, out)
    finally:
        os.environ.pop("ZODIFY_BENCH_VAR", None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
