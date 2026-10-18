# Getting started

Install zodify, validate a dict, and handle a validation error.

HTML: https://zodify.dev/docs/getting-started/

Released zodify 0.8.0; Python >=3.10; alpha. Release manifest verified 2026-09-09.

## Install zodify

Use a virtual environment with Python 3.10 or later. Pin 0.8.0 to run the same release as these examples.

```sh
python -m pip install zodify==0.8.0
```

## Validate a dict and read the result

Pass the schema first and the data second. Valid input returns a dict; invalid input raises ValueError. This example prints both the successful result and the error for a string where an int is expected.

```python
from zodify import validate

schema = {"name": str, "age": int}
print(validate(schema, {"name": "Ada", "age": 36}))

try:
    validate(schema, {"name": "Ada", "age": "36"})
except ValueError as error:
    print(f"ValueError: {error}")
```

Expected output:

```text
{'name': 'Ada', 'age': 36}
ValueError: age: expected int, got str
```

[Download Python example](https://zodify.dev/examples/quickstart.py)

- [Schema grammar](https://zodify.dev/docs/schemas/)
- [Structured errors](https://zodify.dev/docs/errors/)

Updated 2026-09-09. [Project source](https://github.com/junyoung2015/zodify).
