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
