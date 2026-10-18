# Choosing a Python validator

A task-based choice between small dict validation and broader validation tools.

HTML: https://zodify.dev/compare/

Released zodify 0.8.0; Python >=3.10; alpha. Release manifest verified 2026-09-09.

## Start with the task

Compare the data shapes, type support, and integrations your application needs. Direct Python checks may be enough for a small task.

| What you need | A useful starting point |
| --- | --- |
| A handful of checks in one place | Direct Python checks; argparse type or choices for simple CLI arguments. |
| Reusable plain-dict validation with zero required runtime dependencies | Zodify: strict types by default, optional conversion, dict-shaped results. |
| Broader typing, serialization, or framework integration | Pydantic. TypeAdapter validates ordinary types without requiring a BaseModel subclass. |
| Validation against a JSON Schema document | A JSON Schema validator that supports the required draft. Zodify exports only a narrow exact subset. |

- [Pydantic TypeAdapter documentation (checked 2026-09-09)](https://pydantic.dev/docs/validation/latest/concepts/type_adapter/)
- [JSON Schema implementations](https://json-schema.org/tools?query=&tooling_type=validator)
- [Benchmark methodology](https://zodify.dev/benchmarks/)

## Try it with your own data

Check both accepted and rejected inputs, the output shape, and how errors fit your application. If performance matters, measure that workload with equivalent behavior; the benchmark guide explains how.

- [Try a complete example](https://zodify.dev/docs/getting-started/)

Updated 2026-09-09. [Project source](https://github.com/junyoung2015/zodify).
