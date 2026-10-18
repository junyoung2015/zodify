# Schemas and predicates

The released dict, list, union, and callable schema grammar.

HTML: https://zodify.dev/docs/schemas/

Released zodify 0.8.0; Python >=3.10; alpha. Release manifest verified 2026-09-09.

## Describe a shape with Python values

A dict maps field names to schemas. A one-element list describes each item in a list. A Python type requires that exact type. PEP 604 unions combine types. Optional wraps an optional field.

Predicates receive the original value and accept it when they return a truthy result. Accepted values are returned unchanged. A predicate should check its own input type before comparing or indexing it.

```python
from zodify import validate

schema = {"users": [{"name": str}], "enabled": bool}
data = {"users": [{"name": "Ada"}], "enabled": True}
print(validate(schema, data))

# A truthy predicate accepts and preserves the original value.
port_schema = {"port": lambda value: type(value) is int and 1 <= value <= 65535}
print(validate(port_schema, {"port": 8080}))
```

Expected output:

```text
{'users': [{'name': 'Ada'}], 'enabled': True}
{'port': 8080}
```

[Download Python example](https://zodify.dev/examples/schemas.py)

## Supported schema shapes

Pass a dict as data and either a dict schema or supported Schema declaration as the schema. Lists with zero or multiple schema items are invalid. Malformed schemas may raise TypeError. Validation has a max_depth option, defaulting to 32; cyclic models and arbitrary typing expressions are not promised.

Dict-shaped and list-shaped validation creates result containers, but leaf objects and defaults can remain shared.

- [Ownership and defaults](https://zodify.dev/docs/optional-and-defaults/)

Updated 2026-09-09. [Project source](https://github.com/junyoung2015/zodify).
