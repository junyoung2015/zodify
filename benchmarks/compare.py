"""Compare current benchmark results against baseline medians.

Emits informational warnings for regressions while failing fast for configuration
errors (bad args, missing/invalid baseline file).
"""

import json
import os
import sys

REL_TOLERANCE = 0.20  # 20% regression tolerance
# Tiny medians are noisy on shared CI runners; require a minimum absolute delta.
ABS_TOLERANCE_FLOOR_MS = 0.0005

BENCHMARK_SPECS = (
    {
        "name": "import",
        "label": "import median",
        "file": "import.json",
        "current_key": "median_ms",
        "baseline_key": "median_ms",
    },
    {
        "name": "validate",
        "label": "validate median",
        "file": "validate.json",
        "current_key": "median_ms",
        "baseline_key": "median_ms",
    },
    {
        "name": "env",
        "label": "env overhead",
        "file": "env.json",
        "current_key": "overhead_ms",
        "baseline_key": "overhead_ms",
    },
)


def usage():
    return (
        "Usage: compare.py --baseline <path> --current <dir> "
        "[--summary <path>]"
    )


def load_json(path):
    with open(path) as f:
        return json.load(f)


def parse_args(argv):
    baseline_path = None
    current_dir = None
    summary_path = None

    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("--baseline", "--current", "--summary"):
            if i + 1 >= len(argv) or argv[i + 1].startswith("--"):
                raise ValueError(f"{arg} requires a value")
            value = argv[i + 1]
            if arg == "--baseline":
                baseline_path = value
            elif arg == "--current":
                current_dir = value
            else:
                summary_path = value
            i += 2
            continue
        raise ValueError(f"Unknown argument: {arg}")

    if not baseline_path or not current_dir:
        raise ValueError("Both --baseline and --current are required")
    return baseline_path, current_dir, summary_path


def compare_metric(name, current_val, baseline_val):
    """Compare a metric and return (passed, message)."""
    if baseline_val <= 0:
        return False, (
            f"  WARNING {name}: invalid baseline ({baseline_val}) - "
            "cannot compare"
        )

    delta = current_val - baseline_val
    pct = (current_val / baseline_val - 1) * 100
    allowed_delta = max(baseline_val * REL_TOLERANCE, ABS_TOLERANCE_FLOOR_MS)
    if delta > allowed_delta:
        return False, (
            f"  WARNING {name}: {current_val:.6f} ms "
            f"(baseline: {baseline_val:.6f} ms, {pct:+.1f}%; "
            f"allowed delta <= {allowed_delta:.6f} ms)"
        )
    return True, (
        f"  OK {name}: {current_val:.6f} ms "
        f"(baseline: {baseline_val:.6f} ms, {pct:+.1f}%)"
    )


def write_summary(summary_path, report):
    if not summary_path:
        return
    summary_dir = os.path.dirname(os.path.abspath(summary_path))
    if summary_dir:
        os.makedirs(summary_dir, exist_ok=True)
    with open(summary_path, "w") as f:
        f.write(report + "\n")


def main():
    try:
        baseline_path, current_dir, summary_path = parse_args(sys.argv[1:])
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        print(usage(), file=sys.stderr)
        return 2

    if not os.path.exists(baseline_path):
        print(f"Error: baseline file not found: {baseline_path}", file=sys.stderr)
        return 2
    if not os.path.isdir(current_dir):
        print(f"Error: current results dir not found: {current_dir}", file=sys.stderr)
        return 2

    try:
        baseline = load_json(baseline_path)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Error: failed to read baseline JSON: {exc}", file=sys.stderr)
        return 2

    lines = ["# Benchmark Comparison Report", ""]
    warnings = 0
    compared = 0
    missing_results = 0
    missing_baseline = 0

    for spec in BENCHMARK_SPECS:
        current_path = os.path.join(current_dir, spec["file"])
        if not os.path.exists(current_path):
            missing_results += 1
            lines.append(f"  SKIP {spec['name']}: no current results")
            continue

        try:
            current = load_json(current_path)
        except (OSError, json.JSONDecodeError) as exc:
            warnings += 1
            lines.append(
                f"  WARNING {spec['name']}: invalid current JSON ({exc})"
            )
            continue

        compared += 1
        baseline_entry = baseline.get(spec["name"])
        if not isinstance(baseline_entry, dict):
            warnings += 1
            missing_baseline += 1
            lines.append(
                f"  WARNING {spec['label']}: baseline entry missing"
            )
        elif spec["baseline_key"] not in baseline_entry:
            warnings += 1
            missing_baseline += 1
            lines.append(
                f"  WARNING {spec['label']}: baseline metric "
                f"'{spec['baseline_key']}' missing"
            )
        elif spec["current_key"] not in current:
            warnings += 1
            lines.append(
                f"  WARNING {spec['label']}: current metric "
                f"'{spec['current_key']}' missing"
            )
        else:
            passed, msg = compare_metric(
                spec["label"],
                current[spec["current_key"]],
                baseline_entry[spec["baseline_key"]],
            )
            lines.append(msg)
            if not passed:
                warnings += 1

        result = current.get("result")
        if result != "PASS":
            warnings += 1
            lines.append(
                f"  WARNING {spec['name']}: benchmark threshold result={result!r}"
            )

    lines.append("")
    if warnings:
        lines.append(f"Total warnings: {warnings}")
    else:
        lines.append("No regressions detected.")

    if compared == 0:
        lines.append(
            "Comparison incomplete: no current benchmark result files were found."
        )
    elif missing_results or missing_baseline:
        lines.append(
            "Comparison incomplete: "
            f"{missing_results} result file(s) missing, "
            f"{missing_baseline} baseline metric(s) missing."
        )

    report = "\n".join(lines)
    print(report)

    try:
        write_summary(summary_path, report)
    except OSError as exc:
        print(f"Error: failed to write summary: {exc}", file=sys.stderr)
        return 2

    # Warnings are informational only by design.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
