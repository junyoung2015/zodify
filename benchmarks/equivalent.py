"""Comparable strict dict-output workloads, with conformance before timing.

Run from an installed environment: python benchmarks/equivalent.py --output FILE
Optional benchmark dependencies: pydantic>=2, typing_extensions. No runtime deps.
"""

import argparse
import gc
import hashlib
import importlib.metadata
import json
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path

from pydantic import ConfigDict, TypeAdapter, with_config
from typing_extensions import TypedDict
import zodify


@with_config(ConfigDict(strict=True, extra="forbid"))
class Flat(TypedDict):
    name: str
    enabled: bool


@with_config(ConfigDict(strict=True, extra="forbid"))
class Nested(TypedDict):
    account: Flat
    tags: list[str]


WORKLOADS = [
    ("flat", {"name": str, "enabled": bool}, Flat,
     {"name": "Alice", "enabled": True},
     [{}, {"name": "Alice", "enabled": 1},
      {"name": b"Alice", "enabled": True},
      {"name": "Alice", "enabled": True, "extra": None}]),
    ("nested_list", {"account": {"name": str, "enabled": bool}, "tags": [str]},
     Nested, {"account": {"name": "Alice", "enabled": True}, "tags": ["a"] * 20},
     [{"account": {}, "tags": []},
      {"account": {"name": "A", "enabled": True, "extra": 1}, "tags": []},
      {"account": {"name": "A", "enabled": True}, "tags": [1]},
      {"account": {"name": "A", "enabled": True}, "tags": ("a",)}]),
]


def measure(fn, iterations, repeats):
    for _ in range(500):
        fn()
    samples = []
    for _ in range(repeats):
        started = time.perf_counter_ns()
        for _ in range(iterations):
            fn()
        samples.append((time.perf_counter_ns() - started) / iterations)
    return {"samples_ns": samples, "median_ns": statistics.median(samples),
            "min_ns": min(samples), "max_ns": max(samples)}


def run(iterations=3000, repeats=9):
    results = {}
    for name, schema, typed, data, invalid in WORKLOADS:
        adapter = TypeAdapter(typed)
        validators = {
            "zodify": lambda value: zodify.validate(schema, value),
            "pydantic_type_adapter": lambda value: adapter.validate_python(value),
        }
        for validator in validators.values():
            result = validator(data)
            assert type(result) is dict and result == data and result is not data
            for bad in invalid:
                try:
                    validator(bad)
                except ValueError:
                    pass
                else:
                    raise AssertionError(f"{name}: negative fixture accepted: {bad!r}")
        results[name] = {
            "negative_fixtures_passed": len(invalid),
            "warm_success": {label: measure(lambda: fn(data), iterations, repeats)
                             for label, fn in validators.items()},
            "pydantic_adapter_setup": measure(lambda: TypeAdapter(typed), 20, repeats),
        }
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = Path(zodify.__file__).parent
    digest = hashlib.sha256()
    for path in sorted(source.glob("*.py")):
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    report = {
        "python": sys.version, "platform": platform.platform(),
        "machine": platform.machine(), "package_path": str(source),
        "runtime_source_sha256": digest.hexdigest(),
        "versions": {name: importlib.metadata.version(name)
                     for name in ("zodify", "pydantic", "pydantic-core", "typing_extensions")},
        "protocol": {"iterations": 3000, "repeats": 9, "warmup": 500,
                     "gc_enabled": gc.isenabled(), "timer": "perf_counter_ns",
                     "power_settings": "not controlled; local macOS machine"},
        "domain": "plain JSON-like dict/list/str/bool values only; strict; unknown keys rejected; new dict output",
        "limitations": ["Synthetic workloads, not observed customer reuse.",
                        "No model construction, coercion, numeric subclasses, JSON parsing or diagnostics comparison.",
                        "Warm successful calls exclude schema/adapter construction; setup reported separately.",
                        "Laptop run, no universal ranking; inspect variability across separate process runs."],
        "workloads": run(),
    }
    report["fresh_process_import"] = {}
    for module in ("zodify", "pydantic"):
        samples = []
        for _ in range(9):
            code = f"import time;t=time.perf_counter_ns();import {module};print(time.perf_counter_ns()-t)"
            samples.append(int(subprocess.check_output([sys.executable, "-c", code], text=True)))
        report["fresh_process_import"][module] = {"samples_ns": samples,
                                                      "median_ns": statistics.median(samples)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(args.output)


if __name__ == "__main__":
    main()
