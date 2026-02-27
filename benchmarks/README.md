# Benchmarks

Performance benchmarks

## Benchmark Protocol

All three benchmarks follow the same protocol:

- **Warmup:** 5 runs (results discarded) — warms interpreter state and filesystem cache
- **Measured:** 30 runs — collect timing data
- **Metric:** `statistics.median()` of measured runs
- **Timer:** `time.perf_counter()` (highest resolution available)
- **Runtime labeling:** scripts print both actual runtime and target environment
- **Target environment:** ubuntu-latest x64, CPython 3.12
- **Noise control:** Use batched iterations (1000 calls per measured run) and report per-call medians

## Running Locally

```bash
python benchmarks/bench_import.py
python benchmarks/bench_validate.py
python benchmarks/bench_env.py
```

Add `--json <path>` to emit machine-readable JSON output:

```bash
python benchmarks/bench_import.py --json out/import.json
```

CLI behavior:

- `--json` requires a path; invalid/unknown arguments exit non-zero
- Parent directories for JSON output are created automatically

## Baseline Comparison

Compare current results against baseline:

```bash
python benchmarks/compare.py \
  --baseline benchmarks/baselines/ci-baseline.json \
  --current benchmarks/out \
  --summary benchmarks/out/summary.md
```

Regression tolerance: 20% over baseline. Warnings are informational only.

Comparison policy details:

- Regression warnings require both:
  - Relative increase over 20%
  - Absolute increase above a tiny floor (`0.0005 ms`) to avoid micro-noise alerts
- Missing baseline file or invalid CLI usage is treated as a configuration error (non-zero exit)
- Missing baseline metrics/current files are reported as **Comparison incomplete**
- Benchmark script threshold `result` values are also surfaced as warnings

## CI Integration

The `benchmark` job in `.github/workflows/ci.yml` runs benchmarks on every push/PR:

- Runs on `ubuntu-latest`, Python 3.12 only
- Parallel to the `test` job (no dependency)
- **Non-gating:** benchmark step uses `continue-on-error: true`
- **Not a required check:** must NOT be listed in branch protection required status checks
- Results uploaded as `benchmark-results` artifact

## Updating Baselines

To refresh `benchmarks/baselines/ci-baseline.json`:

1. Run benchmarks locally or in CI to get current medians
2. Update values in `ci-baseline.json` with the new medians
3. Commit the updated baseline
