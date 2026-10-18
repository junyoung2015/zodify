# Validation for Python dictionaries

Validate configuration and script inputs using ordinary Python types. Zero required runtime dependencies.

HTML: https://zodify.dev/

Released zodify 0.8.0; Python >=3.10; alpha. Release manifest verified 2026-09-09.

## Your first validation

```python
from zodify import validate

schema = {"port": int, "debug": bool}
data = {"port": 8080, "debug": False}

print(validate(schema, data))
```

Expected output:

```text
{'port': 8080, 'debug': False}
```

[Download Python example](https://zodify.dev/examples/first-validation.py)

## When to use zodify

Use it when you have a Python dict and want a readable, reusable check. Start with ordinary types; add nested shapes, optional keys, or explicit conversions when you need them.

| Try zodify when… | Another approach may fit when… |
| --- | --- |
| You want reusable checks for dictionaries. | A few direct Python checks already solve the task. |
| You validate configuration or script inputs. | Your framework already handles validation. |
| Zero required runtime dependencies matter. | You need broader typing, models, or serialization. |

- [Choosing a validator](https://zodify.dev/compare/)

## Validation errors

An invalid field raises an error with its path. Here, port needs an int, but the input contains a string. Pass an integer, or choose coerce=True when string conversion is intended.

```python
from zodify import validate

try:
    validate({"port": int}, {"port": "8080"})
except ValueError as error:
    print(f"ValueError: {error}")
```

Expected output:

```text
ValueError: port: expected int, got str
```

[Download Python example](https://zodify.dev/examples/invalid-input.py)

- [Types and conversion](https://zodify.dev/docs/types-and-coercion/)

## Default behavior

Types are strict and extra keys are rejected. Optional keys and nullable values are separate choices. Defaults are trusted: they are inserted without validation or copying, so mutable defaults can be shared.

Plain dict schemas return dicts. Optional class declarations provide attribute access.

- [Defaults and ownership](https://zodify.dev/docs/optional-and-defaults/)
- [Optional class syntax](https://zodify.dev/docs/class-schemas/)

Updated 2026-09-09. [Project source](https://github.com/junyoung2015/zodify).
