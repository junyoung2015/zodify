# Documentation

Start with one dict, follow a task guide, or look up a specific validation rule.

HTML: https://zodify.dev/docs/

Released zodify 0.8.0; Python >=3.10; alpha. Release manifest verified 2026-09-09.

## Installation

No extra packages required.

```sh
pip install zodify
```

- [Follow the getting-started guide](https://zodify.dev/docs/getting-started/)

## Basic validation

Pass the schema first, data second. Types are strict; extra keys are rejected.

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

- [First validation](https://zodify.dev/docs/getting-started/)

## Supported types

Use exact Python types, nested dict schemas, one-element list schemas, unions, and predicates.

- [Schema grammar](https://zodify.dev/docs/schemas/)
- [Types and coercion](https://zodify.dev/docs/types-and-coercion/)

## Optional keys and defaults

Optional controls missing keys; a union with None controls nullable values. Defaults are inserted as supplied, without copying or validation.

- [Optional and defaults](https://zodify.dev/docs/optional-and-defaults/)

## Unions

With coercion enabled, string input follows declared union order; non-string exact matches take precedence.

- [Conversion rules](https://zodify.dev/docs/types-and-coercion/)

## Nested schemas

Dict shapes and one-element list schemas validate nested containers. The default maximum depth is 32.

- [Schemas](https://zodify.dev/docs/schemas/)

## Optional class syntax

Schema declarations offer attribute access using the same validation engine.

- [Class schemas and limitations](https://zodify.dev/docs/class-schemas/)

## Custom validators

Predicates return truthy for acceptance; they receive and preserve the original value. Callback errors may expose their own messages.

- [Predicates](https://zodify.dev/docs/schemas/)
- [Error privacy](https://zodify.dev/docs/errors/)

## Environment variables

The env(name, cast, default) helper reads process environment variables. The load_env(path, schema=...) helper parses a .env file without mutating os.environ; with a schema it defaults to coercion and stripping unknown keys. Raw mode returns parsed strings.

- [Configuration recipe](https://zodify.dev/guides/config-validation/)
- [Feature availability](https://zodify.dev/roadmap/)

## Error handling

Text mode raises ValueError. Choose error_mode="structured" for ValidationError. Review error contents before logging them.

- [Errors](https://zodify.dev/docs/errors/)

## Structured errors

ValidationError.issues retains path, message, expected, and got fields. Engine structured errors also expose immutable canonical details with machine codes and typed locations; manually constructed legacy errors can have details=None.

- [Structured error example](https://zodify.dev/docs/errors/)

## Task guides

Choose the input you are working with. Each guide includes a complete example and explains its limits.

- [Configuration](https://zodify.dev/guides/config-validation/)
- [Command-line input](https://zodify.dev/guides/cli-input-validation/)
- [JSON objects](https://zodify.dev/guides/json-object-validation/)

Updated 2026-09-09. [Project source](https://github.com/junyoung2015/zodify).
