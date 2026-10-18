# Missing keys, None, and defaults

Distinguish optional keys from nullable values and understand released default ownership.

HTML: https://zodify.dev/docs/optional-and-defaults/

Released zodify 0.8.1; Python >=3.10; alpha. Release manifest verified 2026-10-18.

## Missing and None are different inputs

Optional(str) permits an absent key, which is omitted from the result. str | None accepts a present null value but still requires the key. Optional(str, 'Ada') inserts a default only when the key is absent.

```python
from zodify import Optional, validate

print(validate({"name": Optional(str)}, {}))
print(validate({"name": str | None}, {"name": None}))
print(validate({"name": Optional(str, "Ada")}, {}))

# Defaults are trusted: neither copied nor validated.
default = []
result = validate({"items": Optional([str], default)}, {})
print("Shares default:", result["items"] is default)
print(validate({"count": Optional(int, "unchecked")}, {}))

try:
    validate({"name": str | None}, {})
except ValueError as error:
    print(f"ValueError: {error}")
```

Expected output:

```text
{}
{'name': None}
{'name': 'Ada'}
Shares default: True
{'count': 'unchecked'}
ValueError: name: missing required key
```

[Download Python example](https://zodify.dev/examples/optional-defaults.py)

## Defaults in the released version

In 0.8.1, a default is inserted as supplied. It is not independently validated or copied. Mutable defaults may be shared between calls. The example shows how an incorrectly typed default is still inserted. Use type-correct defaults in application code.

Prefer immutable, type-correct defaults and construct fresh mutable values in application code. Check the compatibility notes for the installed release before changing a default policy.

- [Roadmap](https://zodify.dev/roadmap/)
- [Schema containers](https://zodify.dev/docs/schemas/)

Updated 2026-10-18. [Project source](https://github.com/junyoung2015/zodify).
