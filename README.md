# zodify

Zod-inspired dict validation for Python. Zero deps. One file.

## Install

```bash
# From PyPI (after publish)
pip install zodify

# From source
pip install ./dist/zodify-0.0.1.tar.gz
```

## Usage

```python
# Use the import that matches your install method:
from zodify import validate, env, count_in_list
# from zodify import validate, env, count_in_list    # PyPI
```

### `validate()` -- Dict Schema Validation

```python
schema = {"port": int, "debug": bool, "name": str}
config = {"port": 8080, "debug": True, "name": "myapp"}

result = validate(schema, config)
# {"port": 8080, "debug": True, "name": "myapp"}

# Coerce strings (great for env vars / config files)
raw = {"port": "8080", "debug": "true", "name": "myapp"}
result = validate(schema, raw, coerce=True)
# {"port": 8080, "debug": True, "name": "myapp"}

# All errors collected at once
validate({"a": int, "b": str}, {"a": "x", "b": 42})
# ValueError: a: expected int, got str
#             b: expected str, got int
```

### `env()` -- Typed Env Var Loading

```python
port = env("PORT", int, default=3000)
debug = env("DEBUG", bool, default=False)
secret = env("SECRET_KEY", str)  # raises if missing
```

### `count_in_list()` -- Count Occurrences

```python
count_in_list(["a", "b", "a"], "a")  # 2
```

## Why zodify?

|                 | zodify      | zon              | zodic            | Pydantic       |
| --------------- | ----------- | ---------------- | ---------------- | -------------- |
| Philosophy      | Minimalist  | Full Zod port    | Full Zod port    | Full ORM       |
| API style       | Plain dicts | Chained builders | Chained builders | Classes        |
| Dependencies    | 0           | 2                | 0                | Many           |
| Code size       | <200 lines  | 1000s+ lines     | 1000s+ lines     | Massive        |
| Learning curve  | Zero        | Must learn DSL   | Must learn DSL   | Must learn DSL |
| Env var support | Yes         | No               | No               | Partial        |

## License

MIT
