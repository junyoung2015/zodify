# Validate a configuration dict

Catch missing keys and misspelled configuration, with an explicit strip alternative.

HTML: https://zodify.dev/guides/config-validation/

Released zodify 0.8.1; Python >=3.10; alpha. Release manifest verified 2026-10-18.

## Validate configuration values

Keep strict validation for configuration that already has Python values. Reject unknown keys to catch misspellings. Insert a simple immutable default only for an intentionally optional setting.

```python
from zodify import Optional, validate

schema = {"host": str, "port": int, "debug": Optional(bool, False)}
config = {"host": "localhost", "port": 8080}
print(validate(schema, config))

with_typo = dict(config, debgu=True)
try:
    validate(schema, with_typo)
except ValueError as error:
    print(f"ValueError: {error}")

# Stripping drops the unknown field from the result.
print(validate(schema, with_typo, unknown_keys="strip"))
print("Original input:", with_typo)
```

Expected output:

```text
{'host': 'localhost', 'port': 8080, 'debug': False}
ValueError: debgu: unknown key
{'host': 'localhost', 'port': 8080, 'debug': False}
Original input: {'host': 'localhost', 'port': 8080, 'debgu': True}
```

[Download Python example](https://zodify.dev/examples/config-validation.py)

## Unknown fields and range checks

unknown_keys='strip' drops unknown fields. Correct misspelled keys in the input to retain their values. Add a predicate to enforce a network-port range; int checks the Python type.

This recipe starts from an existing dict. Handle env-file loading, secrets, and configuration precedence separately.

- [Schema predicates](https://zodify.dev/docs/schemas/)
- [Defaults](https://zodify.dev/docs/optional-and-defaults/)

Updated 2026-09-09. [Project source](https://github.com/junyoung2015/zodify).
