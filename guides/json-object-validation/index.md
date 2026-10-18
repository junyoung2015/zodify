# Validate a JSON object

Parse JSON with the standard library, enforce an object root, then validate Python fields.

HTML: https://zodify.dev/guides/json-object-validation/

Released zodify 0.8.1; Python >=3.10; alpha. Release manifest verified 2026-10-18.

## Parsing and validation are separate steps

Use json.loads() to parse the text, check for an object root, then validate its fields. Invalid JSON and a valid JSON object with incorrect fields fail at different boundaries.

```python
import json
from zodify import validate

def read_user(text):
    data = json.loads(text)
    if type(data) is not dict:
        raise ValueError("Expected a JSON object")
    return validate({"name": str, "age": int}, data)

print(read_user('{"name":"Ada","age":36}'))
for text in ['[]', '{"name":"Ada","age":"36"}', '{"name":']:
    try:
        read_user(text)
    except json.JSONDecodeError as error:
        print(f"JSONDecodeError: {error.msg}")
    except ValueError as error:
        print(f"ValueError: {error}")
```

Expected output:

```text
{'name': 'Ada', 'age': 36}
ValueError: Expected a JSON object
ValueError: age: expected int, got str
JSONDecodeError: Expecting value
```

[Download Python example](https://zodify.dev/examples/json-object-validation.py)

## Parser behavior

The standard parser keeps the last duplicate object key and accepts non-finite numeric constants by default. Set input-size limits before parsing untrusted payloads.

The int schema rejects a parsed 1.0 because it is a Python float. For a general JSON Schema contract, use a JSON Schema validator. The released zodify.json_io.validate_json helper provides a stricter parsing boundary than this standard-library recipe: it rejects duplicate keys, BOMs, nonfinite values and non-object roots before ordinary validation. zodify.json_schema.export_json_schema exports only the exact supported subset; numeric types, defaults, arbitrary predicates and bare containers are refused. The root to_json_schema facade returns only the document.

- [Exact integers and JSON Schema](https://zodify.dev/articles/python-integers-and-json/)
- [Selection guide](https://zodify.dev/compare/)

Updated 2026-09-09. [Project source](https://github.com/junyoung2015/zodify).
