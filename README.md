<!-- logo placeholder: replace with your logo asset -->
<!-- <p align="center">
  <img src="docs/assets/logo.svg" alt="zodify" width="320" />
</p> -->

<h1 align="center">zodify</h1>

<p align="center">
  <strong>Zod-inspired dict validation for Python. Zero deps. One file.</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/zodify/"><img src="https://img.shields.io/pypi/v/zodify?color=blue" alt="PyPI version" /></a>
  <a href="https://pypi.org/project/zodify/"><img src="https://img.shields.io/pypi/pyversions/zodify" alt="Python versions" /></a>
  <a href="https://github.com/junyoung2015/zodify/blob/main/LICENSE"><img src="https://img.shields.io/github/license/junyoung2015/zodify" alt="License" /></a>
</p>

---

**Note:** zodify is in alpha. The API is minimal and may change. Feedback and contributions are welcome!

---

## Quick Start

```python
from zodify import validate

config = validate(
    {"port": int, "debug": bool},
    {"port": 8080, "debug": True},
)
```

That's it. Plain dicts in, validated dicts out. No classes, no DSL, no dependencies.

---

## Why zodify?

Most validation libraries ask you to learn a new DSL or model system. zodify doesn't.

|                 | zodify       | zon              | zodic            | Pydantic       |
| --------------- | ------------ | ---------------- | ---------------- | -------------- |
| Philosophy      | Minimalist   | Full Zod port    | Full Zod port    | Full ORM       |
| API style       | Plain dicts  | Chained builders | Chained builders | Classes        |
| Dependencies    | **0**        | 2                | 0                | Many           |
| Code size       | **~250 LOC** | 1,000s+ LOC      | 1,000s+ LOC      | Large          |
| Learning curve  | **Zero**     | Must learn DSL   | Must learn DSL   | Must learn DSL |
| Env var support | **Built-in** | No               | No               | Partial        |

---

## Install

```bash
pip install zodify
```

> Requires Python 3.10+
>
> To install from source:
>
> ```bash
> git clone https://github.com/junyoung2015/zodify.git && pip install ./zodify
> ```

---

## Usage

### `validate()` — Dict Schema Validation

Define a schema as a plain dict of `key: type` pairs, then validate any dict against it.

```python
from zodify import validate

schema = {"port": int, "debug": bool, "name": str}

# Exact type match
result = validate(schema, {"port": 8080, "debug": True, "name": "myapp"})
# → {"port": 8080, "debug": True, "name": "myapp"}

# Coerce strings — great for env vars and config files
raw = {"port": "8080", "debug": "true", "name": "myapp"}
result = validate(schema, raw, coerce=True)
# → {"port": 8080, "debug": True, "name": "myapp"}

# All errors are collected at once
validate({"a": int, "b": str}, {"a": "x", "b": 42})
# ValueError: a: expected int, got str
#             b: expected str, got int
```

**Parameters:**

| Param          | Type   | Default    | Description                                           |
| -------------- | ------ | ---------- | ----------------------------------------------------- |
| `schema`       | `dict` | —          | Mapping of keys to expected types (`str`, `int`, ...) |
| `data`         | `dict` | —          | The dict to validate                                  |
| `coerce`       | `bool` | `False`    | Cast string values to the target type when possible   |
| `max_depth`    | `int`  | `32`       | Maximum nesting depth to prevent stack overflow       |
| `unknown_keys` | `str`  | `"reject"` | How to handle extra keys: `"reject"` or `"strip"`     |

**Behavior:**

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

### Union Types

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

> **Note:** When `str` is a union member and `coerce=True`, `str` acts as a catch-all fallback — any value that fails earlier union members will coerce via `str()` (e.g., `int | str` with `True` produces `"True"`). Place `str` last in unions to use it as a deliberate fallback, or first to prefer string preservation.

> Requires Python 3.10+ (for `X | Y` union syntax).

---

### Nested Dict Validation

Your schema can contain nested dicts — validation recurses automatically.

```python
schema = {"db": {"host": str, "port": int}}

validate(schema, {"db": {"host": "localhost", "port": 5432}})
# → {"db": {"host": "localhost", "port": 5432}}

validate(schema, {"db": {"host": "localhost", "port": "bad"}})
# ValueError: db.port: expected int, got str
```

Errors use dot-notation paths: `db.host`, `a.b.c`, etc.

---

### Optional Keys

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

> **Note:** `Optional` shadows `typing.Optional`. If you use both in the same file, alias it: `from zodify import Optional as Opt` or use `zodify.Optional(...)`.

---

### List Element Validation

Use a single-element list as the schema value to validate every element in the list.

```python
validate({"tags": [str]}, {"tags": ["python", "config"]})
# → {"tags": ["python", "config"]}

validate({"tags": [str]}, {"tags": ["ok", 42]})
# ValueError: tags[1]: expected str, got int
```

List of dicts works too:

```python
validate(
    {"users": [{"name": str, "age": int}]},
    {"users": [{"name": "Alice", "age": 30}]},
)
```

---

### Combined Example

All features compose naturally:

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

### `env()` — Typed Environment Variables

Read and type-cast environment variables with a single call.

```python
from zodify import env

port   = env("PORT", int, default=3000)
debug  = env("DEBUG", bool, default=False)
secret = env("SECRET_KEY", str)  # raises ValueError if missing
```

**Parameters:**

| Param     | Type   | Default  | Description                                                                                       |
| --------- | ------ | -------- | ------------------------------------------------------------------------------------------------- |
| `name`    | `str`  | —        | Environment variable name                                                                         |
| `cast`    | `type` | —        | Target type (`str`, `int`, `float`, `bool`)                                                       |
| `default` | any    | _(none)_ | Fallback if the var is unset. **Not type-checked** — ensure your default matches the `cast` type. |

---

## Release Process

Release automation is tag-driven:

- Pushing a tag that matches `v*` triggers `.github/workflows/publish.yml`.
- The workflow runs tests, builds distributions, publishes to PyPI, and creates a GitHub Release.
- GitHub Release notes are sourced from the matching section in `CHANGELOG.md` (for example, `## [v0.1.0]`).

Run local preflight before tagging:

```bash
./scripts/release_preflight.sh
```

If preflight passes, push the version tag:

```bash
git tag v0.3.0
git push origin v0.3.0
```

---

## Roadmap

zodify is in **alpha** (v0.3.0). The API surface is small and may evolve. See [`CHANGELOG.md`](CHANGELOG.md) for version-by-version details.

**Shipped:**

- [x] Nested schema validation with dot-path errors
- [x] Optional keys with defaults
- [x] List element validation (including list-of-dicts)
- [x] Custom validator functions
- [x] `unknown_keys` parameter (`"reject"` / `"strip"`)
- [x] `max_depth` recursion depth limit
- [x] Performance benchmark infrastructure
- [x] PEP 561 `py.typed` marker & inline type annotations
- [x] `@overload` signatures for `env()` (IDE type inference)
- [x] Google-style docstrings on all public API symbols
- [x] mypy (strict) & pyright CI gates
- [x] Union type schemas (`str | int` syntax) with left-to-right coercion priority

**Near-term:**

- [ ] Chained builder API

**Exploring:**

- [ ] `.env` file loading
- [ ] JSON Schema export
- [ ] Framework integrations (FastAPI, Django)
- [ ] Async validation support

---

## License

[MIT](LICENSE) — 2026 Jun Young Sohn
