# zodify

Validation for Python dictionaries.

zodify validates configuration and script inputs using ordinary Python types.
It is written in pure Python with zero required runtime dependencies.

[Documentation](https://zodify.dev/docs/) |
[Choosing a validator](https://zodify.dev/compare/) |
[PyPI](https://pypi.org/project/zodify/) |
[Changelog](https://github.com/junyoung2015/zodify/blob/main/CHANGELOG.md)

## Install

```bash
pip install zodify
```

Supports Python 3.10–3.13. The project is in alpha. These examples describe 0.8.0,
published and verified September 9, 2026. See the
[compatibility contract](https://github.com/junyoung2015/zodify/blob/main/API_CONTRACT.md)
for supported behavior and the path to 1.0.

## Quick Start

```python
from zodify import validate

schema = {"port": int, "debug": bool}

validate(schema, {"port": 8080, "debug": False})
# {'port': 8080, 'debug': False}

validate(schema, {"port": "8080", "debug": False})
# ValueError: port: expected int, got str
```

A dictionary schema returns a new dictionary. Types are strict by default:
`"8080"` is a string, so it fails an `int` check. Failures raise `ValueError`
with a path to the field. Extra keys are rejected.

## Choosing a validator

| Use cases for zodify | Reasons to consider another approach |
| --- | --- |
| You already have dictionaries and want reusable checks. | A few direct Python checks already solve the task. |
| You validate configuration, CLI input, or data in scripts. | Your framework already provides the validation you need. |
| Zero required runtime dependencies matter. | You need a broader annotation vocabulary, model features, or specialized serialization. |

Pydantic supports both models and `TypeAdapter` for ordinary types, including
dictionaries. Use a dedicated JSON Schema implementation when a JSON Schema
document is your validation language. The
[comparison guide](https://zodify.dev/compare/) explains the tradeoffs.

## Schemas

Use nested dictionaries, single-element lists, unions, and optional keys as needed:

```python
from zodify import Optional, validate

schema = {
    "db": {"host": str, "port": Optional(int, 5432)},
    "tags": [str],
    "debug": Optional(bool, False),
}

validate(schema, {"db": {"host": "localhost"}, "tags": ["prod"]})
# {'db': {'host': 'localhost', 'port': 5432}, 'tags': ['prod'], 'debug': False}
```

Conversions are explicit. For string inputs such as configuration values:

```python
validate({"port": int}, {"port": "8080"}, coerce=True)
# {'port': 8080}
```

[Schema grammar](https://zodify.dev/docs/schemas/) and
[conversion rules](https://zodify.dev/docs/types-and-coercion/) cover the details.

## Validation behavior

- Strict types: ordinary validation does not coerce values. `bool` and `int`
  are distinct. Set `coerce=True` to opt into the documented conversions.
- Unknown keys: rejected by default. `unknown_keys="strip"` drops them.
- Missing versus null: `Optional(type)` permits omission; `type | None`
  permits a null value. These are separate choices.
- Default ownership: defaults are trusted, without validation or copying.
  Mutable defaults can be shared between results. Successful validation does not
  make data deeply immutable.
- Errors: text mode raises `ValueError`. With `error_mode="structured"`,
  `ValidationError` adds legacy `.issues` and canonical `.details`.
- Depth: `max_depth=32` counts shaped dictionary traversals, including the
  root. It does not limit list nesting, input size, or general resource use.

See [defaults and ownership](https://zodify.dev/docs/optional-and-defaults/) and
[error handling](https://zodify.dev/docs/errors/).

## Optional class syntax

For attribute access, declare a supported `Schema`:

```python
from zodify import Schema, validate

class Config(Schema):
    port: int
    debug: bool = False

config = validate(Config, {"port": 8080})
print(config.port)  # 8080
```

Validate class declarations with `validate(Config, data)`. Direct `Config()`
instantiation is unsupported. Annotations are limited to the documented subset.
See [class schemas and limitations](https://zodify.dev/docs/class-schemas/).

## Guides and reference

| Task | Guide |
| --- | --- |
| Run your first validation | [Getting started](https://zodify.dev/docs/getting-started/) |
| Validate application configuration | [Configuration guide](https://zodify.dev/guides/config-validation/) |
| Validate command-line input | [CLI guide](https://zodify.dev/guides/cli-input-validation/) |
| Parse and validate a JSON object | [JSON input guide](https://zodify.dev/guides/json-object-validation/) |
| Look up options, env parsing, errors, or JSON export limits | [Full API reference](https://github.com/junyoung2015/zodify/blob/main/reference/api.md) |
| Run complete examples | [Example scripts](https://github.com/junyoung2015/zodify/tree/main/examples) |

`env()` reads one variable; `load_env()` parses an env file without changing the
process environment. In schema mode, `load_env()` defaults to coercion and unknown-key
stripping, unlike ordinary validation. Env file loading, canonical details, and
conservative JSON input/export require 0.8.0; the quickstart also works with 0.6.0.

## Project and contributions

Read the [contributor guide](https://github.com/junyoung2015/zodify/blob/main/CONTRIBUTING.md)
for local checks and the
[release procedure](https://github.com/junyoung2015/zodify/blob/main/release-notes/RELEASING.md)
for publication. Report problems in
[GitHub Issues](https://github.com/junyoung2015/zodify/issues).

[Benchmark methodology](https://zodify.dev/benchmarks/) documents the measured
workloads and comparison limits. The
[roadmap](https://zodify.dev/roadmap/) distinguishes released features from plans.
Compilation remains outside the public API. The
[implementation issue](https://github.com/junyoung2015/zodify/issues/6) tracks direction.

## License

[MIT](https://github.com/junyoung2015/zodify/blob/main/LICENSE)

Copyright 2026 Jun Young Sohn.
