# Exact types, coercion, and unions

Understand bool versus int, string conversion, and union order in zodify 0.8.0.

HTML: https://zodify.dev/docs/types-and-coercion/

Released zodify 0.8.0; Python >=3.10; alpha. Release manifest verified 2026-09-09.

## Exact Python types by default

The int schema accepts an actual int. It rejects bool, float, and string values, even when they look numerically equivalent. Coercion is an explicit option.

With coerce=True, string input can convert to int or float. Boolean strings are case-insensitive true/1/yes and false/0/no. Strings are not trimmed by the boolean rule. Conversion to str uses str(value); numeric schemas do not accept arbitrary constructor casting from non-string input.

```python
import json
from zodify import validate

for token in ["1", "1.0", "true", '"1"']:
    try:
        result = validate({"count": int}, {"count": json.loads(token)})
        print(f"{token}: {result}")
    except ValueError as error:
        print(f"{token}: {error}")

print(validate({"port": int}, {"port": "8080"}, coerce=True))
# Union order controls conversion of string inputs.
print(validate({"value": int | str}, {"value": "1"}, coerce=True))
print(validate({"value": str | int}, {"value": "1"}, coerce=True))
```

Expected output:

```text
1: {'count': 1}
1.0: count: expected int, got float
true: count: expected int, got bool
"1": count: expected int, got str
{'port': 8080}
{'value': 1}
{'value': '1'}
```

[Download Python example](https://zodify.dev/examples/exact-types.py)

## Union order can change string results

In coercing unions, exact non-string matches win first. String input then tries union members in their declared order: int | str can turn '1' into 1, while str | int preserves '1'. Without coercion, exact membership determines acceptance. Keep union order consistent when relying on string conversion.

- [JSON integer semantics explained](https://zodify.dev/articles/python-integers-and-json/)
- [CLI recipe](https://zodify.dev/guides/cli-input-validation/)

Updated 2026-09-09. [Project source](https://github.com/junyoung2015/zodify).
