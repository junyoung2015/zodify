from zodify import validate

schema = {"name": str, "age": int}
assert validate(schema, {"name": "Ada", "age": 36}) == {"name": "Ada", "age": 36}
try:
    validate(schema, {"name": "Ada", "age": "36"})
except ValueError:
    pass  # String input is rejected by default.
else:
    raise AssertionError("Expected validation failure")
print("quickstart: passed")
