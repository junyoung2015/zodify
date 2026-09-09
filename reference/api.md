# API reference

Detailed usage for zodify 0.8.0. Start with the [quickstart](../README.md#quick-start)
or the [getting-started guide](https://zodify.dev/docs/getting-started/).
The [API and compatibility contract](../API_CONTRACT.md) defines the supported
surface and compatibility commitments. This release is alpha.
Key-sensitive inference for arbitrary dictionaries is outside the `py.typed` support contract.

## Contents

- [Dict validation](#validate---dict-schema-validation)
- [Reusable configuration](#configuration)
- [Class schemas](#class-based-schemas)
- [JSON Schema export](#json-schema-export-080)
- [JSON object input](#json-object-input-080)
- [Canonical details](#canonical-details-080) and [structured errors](#structured-errors)
- [Union types](#union-types)
- [Nested dictionaries](#nested-dict-validation) and [composition](#schema-composition)
- [Optional keys](#optional-keys)
- [List elements](#list-element-validation)
- [Combined example](#combined-example)
- [Environment variables](#env---typed-environment-variables)
- [Env files](#env-file-loading)

## `validate()` - Dict Schema Validation

Define a schema as a plain dict of `key: type` pairs, then validate any dict against it.

```python
from zodify import validate

schema = {"port": int, "debug": bool, "name": str}

# Exact type match
result = validate(schema, {"port": 8080, "debug": True, "name": "myapp"})
# → {"port": 8080, "debug": True, "name": "myapp"}

# Convert string inputs explicitly
raw = {"port": "8080", "debug": "true", "name": "myapp"}
result = validate(schema, raw, coerce=True)
# → {"port": 8080, "debug": True, "name": "myapp"}

# All errors are collected at once
validate({"a": int, "b": str}, {"a": "x", "b": 42})
# ValueError: a: expected int, got str
#             b: expected str, got int
```

Parameters:

| Param          | Type   | Default    | Description                                           |
| -------------- | ------ | ---------- | ----------------------------------------------------- |
| `schema`       | `dict` | -          | Mapping of keys to expected types (`str`, `int`, ...) |
| `data`         | `dict` | -          | The dict to validate                                  |
| `coerce`       | `bool` | `False`    | Cast string values to the target type when possible   |
| `max_depth`    | `int`  | `32`       | Maximum shaped dictionary traversals, including the root       |
| `unknown_keys` | `str`  | `"reject"` | How to handle extra keys: `"reject"` or `"strip"`     |
| `error_mode`   | `str`  | `"text"`   | Error output format: `"text"` or `"structured"`       |

Behavior:

`max_depth` counts shaped dictionary traversals, including the root. It does not
bound list nesting, parser allocation, callback execution time, or input size.

- Extra keys in `data` are rejected by default (`unknown_keys="reject"`).
- Use `unknown_keys="strip"` to silently drop extra keys and return only schema-declared keys.
- Missing keys raise `ValueError`.
- When `coerce=True`, only `str` inputs are coerced to `int`, `float`, or `bool` (non-string mismatches still error). For `str` targets, any value is accepted via Python's `str()` builtin.
- Bool coercion accepts: `true/false`, `1/0`, `yes/no` (case-insensitive).

```python
# Default: reject unknown keys
validate({"name": str}, {"name": "kai", "age": 25})
# ValueError: age: unknown key

# Opt-in: strip unknown keys
validate(
    {"name": str},
    {"name": "kai", "age": 25},
    unknown_keys="strip",
)
# -> {"name": "kai"}
```

---

## Configuration

`validate()` remains the recommended starting point. Use `Validator` when you repeatedly apply the same options and want reusable defaults.

```python
from zodify import Validator

validator = Validator(
    coerce=True,
    max_depth=16,
    unknown_keys="strip",
    error_mode="structured",
)

result = validator.validate(
    {"port": int, "debug": bool},
    {"port": "8080", "debug": "true", "unused": "x"},
)
# -> {"port": 8080, "debug": True}
```

Per-call keyword arguments override instance defaults for that call only:

```python
from zodify import Validator

validator = Validator(coerce=False, unknown_keys="reject")

# Temporary override for one call:
result = validator.validate(
    {"port": int},
    {"port": "8080"},
    coerce=True,
)
# -> {"port": 8080}

# Defaults remain unchanged:
validator.validate({"port": int}, {"port": "8080"})
# ValueError: port: expected int, got str
```

---

## Class-Based Schemas

`Schema` declarations provide typed attribute access and use the same validation
engine as dictionary schemas.

```python
from zodify import Optional, Schema, Validator, validate

dict_schema = {
    "host": str,
    "port": Optional(int, 5432),
}


class DBConfig(Schema):
    host: str
    port: int = 5432


payload = {"host": "db.local"}

assert validate(dict_schema, payload) == {"host": "db.local", "port": 5432}

db = validate(DBConfig, payload)
assert db.host == "db.local"
assert db["port"] == 5432

validator = Validator(unknown_keys="strip")
assert validator.validate(DBConfig, {"host": "db.local", "extra": "x"}).host == "db.local"
```

The class and dict forms are equivalent for the same structure:

```python
from zodify import Optional, Schema

db_dict_schema = {
    "host": str,
    "port": Optional(int, 5432),
}


class DBConfig(Schema):
    host: str
    port: int = 5432
```

Nested composition works the same way:

```python
from zodify import Schema, validate


class Credentials(Schema):
    username: str
    password: str


class DatabaseConfig(Schema):
    host: str
    port: int = 5432
    creds: Credentials


class AppConfig(Schema):
    name: str
    db: DatabaseConfig


app = validate(
    AppConfig,
    {
        "name": "api",
        "db": {
            "host": "localhost",
            "creds": {"username": "svc", "password": "secret"},
        },
    },
)

assert app.db.host == "localhost"
assert app.db.creds.username == "svc"
```

Class syntax supports autocomplete and attribute access for fields with valid
Python identifiers. Plain dict schemas support arbitrary field names and callable
field validators.

Currently supported:

- Direct annotations for primitive fields
- Default values compiled into `Optional(...)`
- Unions whose members are plain runtime types (for example `str | int` or `int | None`)
- Typed lists, bare `dict`, and bare `list`
- Nested `Schema` subclasses resolved at class-definition time
- Wrapped nested results for nested `Schema` fields and `list[Schema]`
- Wrapped results preserve Schema-origin nesting across `|` and `|=` dict merges
- Non-dict operands on `|` still raise `TypeError`, matching plain `dict` semantics

Current unsupported boundaries:

- Later-defined forward references and self-referential schemas
- Postponed string annotations
- Inheritance beyond direct `class X(Schema): ...`
- Unions containing nested `Schema` subclasses or parameterized container members
- Parameterized `dict[K, V]` annotations
- Invalid identifier field names
- Dict-method field names such as `items`, `keys`, and `values`
- Callable validators in the class body
- `model_config`-style options and custom metaclass APIs
- User-facing registries and caching layers
- Direct `MySchema()` instantiation; validate class declarations with `validate(MySchema, data)`

Notes:

- `ValidatedDict` is an internal runtime carrier. Its import is outside the public API.
- Only annotated fields become schema fields. Unannotated control objects such as `model_config`, `registry`, or `cache` stay inert plain class attributes and are not interpreted by zodify.
- If you need dict-method field names or unsupported union members, stay on plain dict schemas.
- Plain dict schemas still return plain `dict` values. Nested plain dict fields stay plain dicts.

---

## JSON Schema Export (0.8.0)

Export the supported input contract over plain JSON-compatible built-in
instances to Draft 2020-12:

```python
from zodify import Optional
from zodify.json_schema import export_json_schema

result = export_json_schema({"host": str, "debug": Optional(bool)})
assert result.fidelity == "exact"
assert result.contract_kind == "input"
assert result.document["additionalProperties"] is False
```

`to_json_schema(schema)` returns the document from a root-level import.
`export_json_schema(schema)` also reports `schema_draft` and `differences`. Exact export
supports shaped objects, strings, booleans, null, homogeneous lists and supported
unions. Optional fields without defaults may be omitted. Nullability does not
make a required key optional.

Unsupported declarations raise `UnsupportedSchemaError` with a schema location.
Numbers, defaults, predicates, bare containers, cycles, non-string keys and
structures outside the ordinary 32-dictionary depth budget or the separate
64-transition preparation cap are rejected. In particular, JSON
Schema integer accepts `1.0`, whereas zodify's exact `int` check rejects it;
JSON Schema default annotations cannot describe insertion of trusted values.
There is no approximation mode, coercion/stripping contract, remote reference
resolver or general JSON Schema validator. No `jsonschema` runtime dependency
is required. See [`examples/json_schema_export.py`](../examples/json_schema_export.py).

## JSON object input (0.8.0)

```python
from zodify.json_io import validate_json

config = validate_json({"port": int}, '{"port": 8080}', max_bytes=1024)
assert config == {"port": 8080}
```

Accepts text or UTF-8 bytes containing one JSON object. Duplicate keys, BOMs,
NaN/infinities and overflowing float tokens are rejected. Optional `max_bytes`
limits encoded input size before parsing; it does not limit decoder allocations,
CPU use or nesting. Counting text bytes needs a UTF-8 encoding allocation.
Parse errors use `JSONInputError` with a generic machine code and optional line
and column; validation errors retain the shared engine's error modes. Neither
tracebacks nor application code should be assumed to redact input automatically.

---

## Canonical details (0.8.0)

Engine errors in structured mode add `error.details`, a tuple of immutable
`ValidationIssue` records containing `code`, typed `loc`, display `path`,
`message`, `expected` and `got`. A key named `"a.b"` has location `("a.b",)`;
a nested key has `("a", "b")`. Codes cover type/union mismatch, missing/unknown
keys, failed coercion/predicates and exceeded depth.

Legacy `.issues` still contains the same four mutable keys and legacy messages.
It is independent of the canonical snapshot. Direct `ValidationError([...])`
construction has `details=None`, as do legacy adapter errors without structural
locations and failures involving unsupported non-string/non-integer mapping keys.
Canonical messages omit raw values and callback exception text; key names and
type labels can still be sensitive. Legacy messages can include raw values.
`copy`, `deepcopy` and `pickle` preserve both views. Consumers should tolerate
future additional codes. The 0.8 serialization interface remains subject to the
pre-1.0 compatibility policy.

## Structured Errors

By default, validation failures raise `ValueError` with human-readable messages.
Set `error_mode="structured"` to receive `ValidationError` exceptions with an
`.issues` list for application error handling.

```python
from zodify import validate, ValidationError

try:
    validate(
        {"port": int, "host": str},
        {"port": "abc", "host": 42},
        error_mode="structured",
    )
except ValidationError as e:
    print(e.issues)
    # [
    #   {"path": "port", "message": "expected int, got str", "expected": "int", "got": "str"},
    #   {"path": "host", "message": "expected str, got int", "expected": "str", "got": "int"},
    # ]
```

`ValidationError` subclasses `ValueError`, so existing `except ValueError` handlers still work. Each issue dict has four keys: `path`, `message`, `expected`, and `got`.

```python
# Works with all error types: type mismatch, missing key, coercion failure,
# custom validator failure, depth exceeded, unknown key, and union mismatch.

# Set conversion, unknown-key, and error options together:
validate(schema, data, coerce=True, unknown_keys="strip", error_mode="structured")
```

---

## Union Types

Use Python's `str | int` syntax to accept multiple types for a single key.

```python
schema = {"value": str | int}

validate(schema, {"value": "hello"})  # → {"value": "hello"}
validate(schema, {"value": 42})       # → {"value": 42}

validate(schema, {"value": 3.14})
# ValueError: value: expected str | int, got float
```

Types are checked left-to-right. With `coerce=True`, type order controls coercion priority:

```python
# str first → "42" stays as string (str coercion matches first)
validate({"value": str | int}, {"value": "42"}, coerce=True)
# → {"value": "42"}

# int first → "42" coerced to int (int coercion matches first)
validate({"value": int | str}, {"value": "42"}, coerce=True)
# → {"value": 42}
```

Union types compose with lists, nested dicts, and `Optional`:

```python
validate({"items": [int | str]}, {"items": ["42"]}, coerce=True)
# → {"items": [42]}

validate({"config": {"v": int | str}}, {"config": {"v": "42"}}, coerce=True)
# → {"config": {"v": 42}}
```

With `coerce=True`, non-string input first uses an exact matching union member.
String inputs try members in order. When conversion reaches a `str` member,
`str()` accepts the value (for example, `int | str` with `True` produces
`"True"`). Place `str` last for fallback conversion, or first to preserve strings.

Requires Python 3.10+ (for `X | Y` union syntax).

---

## Nested Dict Validation

Validation recurses through nested dictionaries in the schema.

```python
schema = {"db": {"host": str, "port": int}}

validate(schema, {"db": {"host": "localhost", "port": 5432}})
# → {"db": {"host": "localhost", "port": 5432}}

validate(schema, {"db": {"host": "localhost", "port": "bad"}})
# ValueError: db.port: expected int, got str
```

Errors use dot-notation paths: `db.host`, `a.b.c`, etc.

---

## Schema Composition

Compose schemas by placing existing schema dictionaries inside other dictionaries.

```python
from zodify import validate

db_schema = {"host": str, "port": int}
credentials_schema = {"username": str, "password": str}
flag_schema = {"beta": bool | str}

service_schema = {
    "name": str,
    "db": db_schema,
    "credentials": credentials_schema,
    "flags": {
        "signup_flow": flag_schema,
    },
}

validate(
    service_schema,
    {
        "name": "api",
        "db": {"host": "localhost", "port": 5432},
        "credentials": {"username": "svc", "password": "secret"},
        "flags": {"signup_flow": {"beta": "true"}},
    },
    coerce=True,
)
```

For the full runnable version, see [`examples/nested_schemas.py`](../examples/nested_schemas.py).

---

## Optional Keys

Use `Optional` to mark keys that can be missing. Provide a default, or omit it to exclude the key from results.

```python
from zodify import validate, Optional

schema = {
    "host": str,
    "port": Optional(int, 8080),     # default 8080
    "debug": Optional(bool),          # absent if missing
}

validate(schema, {"host": "localhost"})
# → {"host": "localhost", "port": 8080}
```

`Optional` shadows `typing.Optional`. If you use both in the same file, alias it: `from zodify import Optional as Opt` or use `zodify.Optional(...)`.

---

## List Element Validation

Use a single-element list as the schema value to validate every element in the list.

```python
validate({"tags": [str]}, {"tags": ["python", "config"]})
# → {"tags": ["python", "config"]}

validate({"tags": [str]}, {"tags": ["ok", 42]})
# ValueError: tags[1]: expected str, got int
```

For a list of dictionaries:

```python
validate(
    {"users": [{"name": str, "age": int}]},
    {"users": [{"name": "Alice", "age": 30}]},
)
```

---

## Combined Example

This example combines nested dictionaries, lists, and optional defaults:

```python
from zodify import validate, Optional

schema = {
    "db": {"host": str, "port": Optional(int, 5432)},
    "tags": [str],
    "debug": Optional(bool, False),
}

validate(schema, {
    "db": {"host": "localhost"},
    "tags": ["prod"],
})
# → {"db": {"host": "localhost", "port": 5432},
#    "tags": ["prod"], "debug": False}
```

---

## `env()` - Typed Environment Variables

Read and type-cast environment variables with a single call.

```python
from zodify import env

port   = env("PORT", int, default=3000)
debug  = env("DEBUG", bool, default=False)
secret = env("SECRET_KEY", str)  # raises ValueError if missing
```

Parameters:

| Param     | Type   | Default  | Description                                                                                       |
| --------- | ------ | -------- | ------------------------------------------------------------------------------------------------- |
| `name`    | `str`  | -        | Environment variable name                                                                         |
| `cast`    | `type` | -        | Target type (`str`, `int`, `float`, `bool`)                                                       |
| `default` | any    | (none) | Fallback if the var is unset. Unchecked. Supply a default that matches the `cast` type. |

---

## `.env` File Loading

Requires 0.8.0. `load_env()` parses an env file and returns its values, with
optional schema validation. It leaves `os.environ` unchanged.

```python
from zodify import load_env

raw = load_env("app.env")
# -> {"PORT": "8080", "DEBUG": "yes"}
```

Pass `schema=` to validate the parsed mapping through the existing `validate()` engine:

```python
from zodify import load_env

config = load_env(
    "app.env",
    schema={"PORT": int, "DEBUG": bool},
)
# -> {"PORT": 8080, "DEBUG": True}
```

To apply reusable validation options, instantiate `Validator` first:

```python
from zodify import Validator, load_env

validator = Validator(coerce=False, unknown_keys="reject")
raw = load_env("app.env")

config = validator.validate(
    {"PORT": int},
    raw,
    coerce=True,
    max_depth=32,
    unknown_keys="strip",
)
# -> {"PORT": 8080}
```

`load_env("app.env", schema=...)` defaults to `coerce=True`, `max_depth=32`, and `unknown_keys="strip"` in schema mode. `validator.validate(schema, load_env(path), ...)` uses the `Validator` instance defaults unless you pass explicit overrides.

Contract notes:

- `path` accepts `str | os.PathLike[str]`. Relative paths resolve from the current working directory.
- Files are read with plain UTF-8 decoding. A leading UTF-8 BOM is preserved, so the first key usually fails as `invalid key` instead of being stripped silently.
- Raw mode returns `dict[str, str]`.
- Schema mode returns the same result shape as `validate()`: a plain dict for dict schemas, or the wrapped schema result for `Schema` subclasses.
- Schema mode defaults to `coerce=True`, `max_depth=32`, and `unknown_keys="strip"`. Pass explicit overrides when you want stricter behavior such as `coerce=False` or `unknown_keys="reject"`.
- Raw mode forbids schema-only kwargs. `load_env("app.env", coerce=True)` raises `TypeError("schema is required when using coerce, max_depth, or unknown_keys")` before file parsing begins.
- `on_missing="raise"` is the default. `on_missing="empty"` suppresses only the missing-file case and still validates an empty mapping when `schema=` is supplied.
- Non-missing I/O failures such as `PermissionError`, `IsADirectoryError`, other `OSError` subclasses, and `UnicodeDecodeError` propagate unchanged.

Parser rules:

- Blank lines are ignored.
- Lines whose first non-whitespace character is `#` are ignored.
- Assignments split on the first `=` only.
- Keys are stripped before validation and must match `[A-Za-z_][A-Za-z0-9_.-]*`.
- Duplicate keys use last assignment wins while preserving the key's original insertion position.
- Quote classification happens after trimming the value fragment once.
- Matching surrounding single or double quotes are removed only when they are the first and last characters of the trimmed value.
- Literal interior quotes stay literal when they remain inside the surrounding pair. For example, `CITY=O'Hare` stays unquoted, while `KEY='"hello"'` becomes `"hello"` because only the surrounding single quotes are removed and zodify does no escape processing.
- `#`, `${VAR}`, and additional `=` characters inside values stay literal.

Exact parser failure messages:

- `missing '='`
- `blank key`
- `invalid key`
- `unmatched surrounding quote`
- `export syntax is unsupported`
- `multiline values are unsupported`
- `unsupported .env syntax`

Parse failures are aggregated in file order. In text mode, all messages are newline-joined in one `ValueError`. In structured mode, zodify raises `ValidationError` with one issue per failure using the resolved path and the exact shape `{"path": "<resolved-path>[line N]", "message": "...", "expected": "valid .env assignment", "got": "<raw line>"}`.

```python
from zodify import ValidationError, load_env

try:
    load_env("app.env", error_mode="structured")
except ValidationError as exc:
    print(exc.issues[0])
    # {
    #   "path": "/absolute/path/app.env[line 1]",
    #   "message": "missing '='",
    #   "expected": "valid .env assignment",
    #   "got": "BROKEN",
    # }
```

Unsupported `load_env()` features:

- Variable expansion.
- Multiline values.
- `export KEY=value` syntax.
- Inline-comment parsing.
- Environment mutation.
- A `Validator.load_env()` method.
