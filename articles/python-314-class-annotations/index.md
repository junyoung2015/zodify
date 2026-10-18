# Python 3.14 class annotations and the empty-schema bug

A standard-library reproduction of deferred annotation discovery, the fix in zodify 0.8.1, and its execution boundary.

HTML: https://zodify.dev/articles/python-314-class-annotations/

Released zodify 0.8.1; Python >=3.10; alpha. Release manifest verified 2026-10-18.

## An annotated field can be absent from the raw namespace

A runtime annotation consumer cannot assume that a class namespace already contains an __annotations__ mapping. Python 3.14 defers annotation evaluation by default. Zodify 0.8.0 read that mapping directly, so an ordinary annotated class could become an empty schema. Version 0.8.1 uses inspect.get_annotations(cls, eval_str=False) to discover the fields.

This standard-library-only reproduction captures the direct lookup before introspection. Reading annotations first can materialize them and hide the difference. Run the file without 'from __future__ import annotations'; that opt-in string behavior is a separate case. The assertions check the version difference and print a stable confirmation. The table records the observed values of direct and resolved on macOS, not additional stdout.

```python
import inspect
import sys

class Port:
    port: int

# Capture the raw namespace before any annotation introspection.
direct = dict(Port.__dict__.get("__annotations__", {}))
resolved = inspect.get_annotations(Port, eval_str=False)

if sys.version_info >= (3, 14):
    assert direct == {}
else:
    assert direct == {"port": int}
assert resolved == {"port": int}
print("Raw namespace matches the interpreter's annotation behavior")
print("get_annotations discovers port: int")
```

Expected output:

```text
Raw namespace matches the interpreter's annotation behavior
get_annotations discovers port: int
```

[Download Python example](https://zodify.dev/examples/annotation-namespace.py)

| Observed CPython | direct before introspection | resolved |
| --- | --- | --- |
| 3.10.19 | {'port': <class 'int'>} | {'port': <class 'int'>} |
| 3.13.11 | {'port': <class 'int'>} | {'port': <class 'int'>} |
| 3.14.6 | {} | {'port': <class 'int'>} |

- [Python 3.14: deferred annotation evaluation](https://docs.python.org/3.14/whatsnew/3.14.html#pep-649-and-pep-749-deferred-evaluation-of-annotations)

## The empty schema changed both acceptance decisions

On macOS CPython 3.14.6, isolated installs of the published releases produced the outcomes below. An empty input incorrectly passed in 0.8.0 because no required field was discovered. Valid input failed because port looked like an unknown key. The comparison fixture asserts both outcomes, including the historical defect when run with 0.8.0. With 0.8.1 it checks required-field rejection and valid-input acceptance.

```python
import sys
from importlib.metadata import version
from zodify import Schema, validate

release = version("zodify")
assert release in {"0.8.0", "0.8.1"}

class Port(Schema):
    port: int

def outcome(data):
    try:
        return dict(validate(Port, data))
    except ValueError as error:
        return str(error)

missing = outcome({})
valid = outcome({"port": 8080})
old_deferred = release == "0.8.0" and sys.version_info >= (3, 14)
assert missing == ({} if old_deferred else "port: missing required key")
assert valid == ("port: unknown key" if old_deferred else {"port": 8080})
print("Missing-field and valid-input checks match the published version")
```

Expected output:

```text
Missing-field and valid-input checks match the published version
```

[Download Python example](https://zodify.dev/examples/annotation-release-comparison.py)

| Published release on CPython 3.14.6 | missing: outcome({}) | valid: outcome({'port': 8080}) |
| --- | --- | --- |
| 0.8.0 | {} | port: unknown key (ValueError) |
| 0.8.1 | port: missing required key (ValueError) | {'port': 8080} |

- [Published 0.8.1 and artifact verification](https://github.com/junyoung2015/zodify/blob/main/release-notes/v0.8.1.md)

## eval_str=False still permits annotation-expression execution

inspect.get_annotations is a standard-library entry point available on the declared supported interpreters. In Python 3.14 it aliases annotationlib.get_annotations. Its default VALUE format retrieves runtime values and can execute deferred annotation expressions. eval_str=False leaves string values such as the quoted 'str' annotation unchanged; it does not suppress execution of field_type(). Annotation introspection is not a sandbox.

In this ordinary class, before is ['evaluated'] on CPython 3.10.19 and 3.13.11, and [] on 3.14.6. After introspection, events is ['evaluated'] on all three, and the quoted label annotation remains a string. Zodify calls introspection during Schema subclass construction, so supported annotation expressions execute at class definition rather than waiting for validate(). Inspect only code you trust to execute.

```python
import inspect
import sys

events = []

def field_type():
    events.append("evaluated")
    return int

class Port:
    port: field_type()
    label: "str"

before = list(events)
resolved = inspect.get_annotations(Port, eval_str=False)
assert before == ([] if sys.version_info >= (3, 14) else ["evaluated"])
assert events == ["evaluated"]
assert resolved == {"port": int, "label": "str"}
print("The annotation expression executed")
print("The quoted annotation stayed a string")
```

Expected output:

```text
The annotation expression executed
The quoted annotation stayed a string
```

[Download Python example](https://zodify.dev/examples/annotation-execution.py)

- [annotationlib.get_annotations: formats, eval_str, and execution](https://docs.python.org/3.14/library/annotationlib.html#annotationlib.get_annotations)
- [Security implications of introspecting annotations](https://docs.python.org/3.14/library/annotationlib.html#security-implications-of-introspecting-annotations)
- [inspect.get_annotations compatibility entry point](https://docs.python.org/3.14/library/inspect.html#inspect.get_annotations)

## The patch preserves the class-schema boundaries

Zodify still requires direct Schema subclasses and concrete supported annotations. Quoted or postponed string annotations, unresolved names, and inheritance beyond a direct subclass fail during class definition. The introspection helper ignores inherited class annotations; using it does not add inherited-schema support. Defaults, unknown-key policy, and the single validation engine retain their existing behavior. Compilation remains unavailable.

These observations use macOS CPython 3.10.19, 3.13.11, and 3.14.6. The linked current Python 3.14 documentation identifies itself as 3.14.8; that is a documentation version, not the tested runtime. Zodify's declared support remains Python 3.10–3.13. This reproduction does not establish a broader Python 3.14, operating-system, free-threaded, or JIT support matrix.

- [Supported class schemas](https://zodify.dev/docs/class-schemas/)
- [Released feature availability](https://zodify.dev/roadmap/)

Updated 2026-10-18. [Project source](https://github.com/junyoung2015/zodify).
