# Validate command-line inputs

Convert argparse strings deliberately and handle invalid command-line values.

HTML: https://zodify.dev/guides/cli-input-validation/

Released zodify 0.8.1; Python >=3.10; alpha. Release manifest verified 2026-10-18.

## Convert at the input boundary

argparse can produce strings; coerce=True lets the validation step explicitly convert supported values. The example supplies an argument list so it runs reproducibly; use parser.parse_args() for real command-line arguments.

```python
import argparse
from zodify import validate

parser = argparse.ArgumentParser()
parser.add_argument("--port", required=True)
parser.add_argument("--debug", default="false")
schema = {"port": int, "debug": bool}
args = vars(parser.parse_args(["--port", "8080", "--debug", "yes"]))
print(validate(schema, args, coerce=True))

try:
    validate(schema, {"port": "not-a-port", "debug": "false"}, coerce=True)
except ValueError as error:
    print(f"ValueError: {error}")
```

Expected output:

```text
{'port': 8080, 'debug': True}
ValueError: port: cannot coerce 'not-a-port' to int
```

[Download Python example](https://zodify.dev/examples/cli-input-validation.py)

## Conversion limits

Add a predicate if a port must fall within a specific range. Boolean conversion recognizes a small vocabulary. Handle errors with an application-controlled message if arguments may contain secrets.

For a single argument, argparse's built-in type or choices may be enough. Use a shared validation schema when the same shape also comes from another boundary.

- [Conversion and union rules](https://zodify.dev/docs/types-and-coercion/)
- [Error privacy](https://zodify.dev/docs/errors/)

Updated 2026-09-09. [Project source](https://github.com/junyoung2015/zodify).
