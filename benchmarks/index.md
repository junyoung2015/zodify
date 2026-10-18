# Benchmarks and measurement

Reproducible measurement requirements and the limits of current performance claims.

HTML: https://zodify.dev/benchmarks/

Released zodify 0.8.1; Python >=3.10; alpha. Release manifest verified 2026-10-18.

## Available measurements

Earlier speed rankings and multipliers have been withdrawn. A comparison needs equivalent behavior and separate setup measurements.

No replacement cross-library ranking is published here. Repository experiments are development evidence and must identify their exact commit and environment before supporting a released-product claim.

- [Benchmark source and artifacts](https://github.com/junyoung2015/zodify/tree/main/benchmarks)
- [Choose by capability](https://zodify.dev/compare/)

## The cost of canonical diagnostics in 0.8.0

Versioned Python 3.12 flat and nested synthetic fixtures compared complete 0.8.0 and 0.6.0 versions on one machine. Structured-mode successful calls increased 36–43% and failed calls 61–64%. Default text-mode successes were approximately unchanged; text-mode failures increased 9–11%. Import median rose from about 2.3 ms to 4.3 ms.

Typed locations require traversal work and failures retain both canonical records and legacy issues. These timings cover the diagnostic implementation and synthetic fixtures on the recorded machine. Application performance and cross-library comparisons need separate measurement. This release uses the ordinary validation engine.

- [0.8.0 release notes](https://github.com/junyoung2015/zodify/blob/main/release-notes/v0.8.0.md)

## A reproducible comparison must include

Record the commit, installed-wheel version and hash, interpreter, platform, dependency versions, repeated raw samples, and the exact success/failure fixtures. Check output equivalence before timing. Include TypeAdapter for the appropriate Pydantic task.

Measure setup separately from repeated validation. Report invalid input, strictness, unknown-key policy, nested shapes, import time, and installed footprint with named metric definitions. Avoid attributing a single scenario's result to every validation workload.

Compilation experiments must report preparation cost, ordinary and prepared call costs, and a measured break-even point. Published APIs are listed with their PyPI release.

- [Released feature availability](https://zodify.dev/roadmap/)
- [An executable semantic comparison](https://zodify.dev/articles/python-integers-and-json/)

Updated 2026-09-09. [Project source](https://github.com/junyoung2015/zodify).
