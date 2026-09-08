# Validation measurements

`equivalent.py` is the maintained comparison. It tests matching required fields,
strict string/boolean acceptance, unknown-key rejection and new dictionary output
before timing. Pydantic uses a reused TypeAdapter over TypedDict, not a model.

Use an isolated installed-wheel environment, install `pydantic` and
`typing_extensions` as benchmark-only dependencies, then run:

```sh
python benchmarks/equivalent.py --output benchmarks/results/equivalent-run1.json
```

Run separate processes at least three times. Raw records include versions,
package location, source digest, warm call samples, setup and fresh-process import.
Failure messages, Python subclasses, numeric semantics, parsing and framework
workloads are not compared. A fresh-process import timer excludes interpreter
startup; TypeAdapter setup is outside successful hot-call timing and reported
separately. Synthetic loops are not evidence of actual application reuse.

Older `comparison_bench.py`, `comp_bench2.py` and prior reports are historical
experiments with non-equivalent constraints/output obligations. Do not use their
rankings or ratios as current product claims. The `bench_*` scripts are internal
regression probes, not cross-library recommendations.

TypeAdapter configuration references:
https://pydantic.dev/docs/validation/latest/api/pydantic/type_adapter/
https://pydantic.dev/docs/validation/latest/api/pydantic/config/
