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
| Code size       | **<200 LOC** | 1,000s+ LOC      | 1,000s+ LOC      | Large          |
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

| Param    | Type   | Default | Description                                           |
| -------- | ------ | ------- | ----------------------------------------------------- |
| `schema` | `dict` | —       | Mapping of keys to expected types (`str`, `int`, ...) |
| `data`   | `dict` | —       | The dict to validate                                  |
| `coerce` | `bool` | `False` | Cast string values to the target type when possible   |

**Behavior:**

- Extra keys in `data` are silently stripped — only schema-declared keys are returned.
- Missing keys raise `ValueError`.
- When `coerce=True`, only `str` inputs are coerced (non-string mismatches still error).
- Bool coercion accepts: `true/false`, `1/0`, `yes/no` (case-insensitive).

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

| Param     | Type   | Default  | Description                                     |
| --------- | ------ | -------- | ----------------------------------------------- |
| `name`    | `str`  | —        | Environment variable name                       |
| `cast`    | `type` | —        | Target type (`str`, `int`, `float`, `bool`)     |
| `default` | any    | _(none)_ | Fallback if the var is unset. Not type-checked. |

---

```python
from zodify import count_in_list

count_in_list(["a", "b", "a", "c"], "a")  # → 2
```

---

## Roadmap

zodify is in **alpha** (v0.0.1). The API surface is small and may evolve.

**Near-term:**

- [ ] Nested schema validation
- [ ] Optional / nullable fields
- [ ] Custom validator functions
- [ ] List item validation

**Exploring:**

- [ ] `.env` file loading
- [ ] JSON Schema export
- [ ] Framework integrations (FastAPI, Django)
- [ ] Async validation support
- [ ] Chained builder API

---

## License

[MIT](LICENSE) — 2026 Jun Young Sohn
