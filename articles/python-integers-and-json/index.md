# Python int and JSON Schema integer

An executable explanation of exact Python types and JSON numeric semantics.

HTML: https://zodify.dev/articles/python-integers-and-json/

Released zodify 0.8.1; Python >=3.10; alpha. Release manifest verified 2026-10-18.

## Parsing integers and floats

In zodify 0.8.1, int means exact Python int. After standard-library JSON parsing, 1 becomes int and 1.0 becomes float. Python bool is also rejected by the int schema. The following example tests all four cases and the opt-in conversion alternative.

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

## JSON Schema integer rules

JSON Schema considers a number with zero fractional part an integer, including 1.0. Python runtime type identity and mathematical integrality are distinct contracts. Translating int directly to a JSON Schema integer constraint does not preserve every acceptance decision.

The released exact exporter refuses numeric declarations because these acceptance rules differ. Use a JSON Schema validator when that standard is the authority for your payload.

- [JSON Schema numeric reference (checked 2026-09-09)](https://json-schema.org/understanding-json-schema/reference/numeric)
- [Download and run the JSON recipe](https://zodify.dev/guides/json-object-validation/)
- [Exact-type reference](https://zodify.dev/docs/types-and-coercion/)

Updated 2026-10-18. [Project source](https://github.com/junyoung2015/zodify).
