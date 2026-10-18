# Optional class schemas

Use Schema for attribute access while keeping the released syntax limits visible.

HTML: https://zodify.dev/docs/class-schemas/

Released zodify 0.8.1; Python >=3.10; alpha. Release manifest verified 2026-10-18.

## Declare fields with Schema

Subclass Schema with concrete field annotations, then call validate(User, data) to get an instance with attributes. Dict schemas use the same validation engine.

```python
from zodify import Schema, validate

class User(Schema):
    name: str
    age: int

user = validate(User, {"name": "Ada", "age": 36})
print(user.name)
print(user.age)
```

Expected output:

```text
Ada
36
```

[Download Python example](https://zodify.dev/examples/class-schemas.py)

## Use the supported subset

Do not assume arbitrary postponed annotations, forward references, recursive models, general inheritance, generics, or every typing construct are supported. The example uses concrete annotations without 'from __future__ import annotations'.

Validator stores reusable validation options. Schema compilation and caching are unavailable in this release.

Version 0.8.1 fixes field discovery under Python 3.14 deferred annotations and evaluates supported annotation expressions at class definition. Fresh PyPI wheel checks passed on macOS CPython 3.14.6. The declared support range remains Python 3.10–3.13; this specific check does not establish broader Python 3.14 support. Unresolved names and unsupported string or postponed annotations still fail at class definition.

- [Dict schema reference](https://zodify.dev/docs/schemas/)
- [Python 3.14 annotation discovery explained](https://zodify.dev/articles/python-314-class-annotations/)
- [Choosing a broader model tool](https://zodify.dev/compare/)

Updated 2026-10-18. [Project source](https://github.com/junyoung2015/zodify).
