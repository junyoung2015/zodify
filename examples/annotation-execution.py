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
