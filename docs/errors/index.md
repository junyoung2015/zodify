# Errors and privacy

Handle text and structured errors and review what their messages contain.

HTML: https://zodify.dev/docs/errors/

Released zodify 0.8.0; Python >=3.10; alpha. Release manifest verified 2026-09-09.

## Choose structured errors explicitly

The default text mode raises ValueError. error_mode='structured' raises ValidationError, a ValueError subclass with an issues list. Each issue carries a string path, message, expected, and got. These legacy fields are preserved. Engine errors also expose a separate immutable details tuple of ValidationIssue records with machine codes and typed locations; manual legacy errors and unsupported key locations may have details=None. The canonical snapshot stays unchanged when issues is mutated.

```python
from zodify import ValidationError, validate

try:
    validate({"port": int}, {"port": "wrong"}, error_mode="structured")
except ValidationError as error:
    print(error.issues[0])
```

Expected output:

```text
{'path': 'port', 'message': 'expected int, got str', 'expected': 'int', 'got': 'str'}
```

[Download Python example](https://zodify.dev/examples/errors.py)

- [Measured diagnostics cost](https://zodify.dev/benchmarks/#diagnostics-cost)

## Treat error text as potentially sensitive

Coercion failures can include the original string, and custom callback exceptions can include callback messages. Avoid logging entire errors for credentials or user secrets; prefer an application-controlled message and a reviewed field identifier.

Legacy paths use dots and brackets. Literal field names containing punctuation can be ambiguous. Use each ValidationIssue record’s loc field in details for structural locations when available.

- [Schema predicates](https://zodify.dev/docs/schemas/)
- [Roadmap](https://zodify.dev/roadmap/)

Updated 2026-09-09. [Project source](https://github.com/junyoung2015/zodify).
