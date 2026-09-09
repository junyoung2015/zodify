from zodify import Optional, validate

assert validate({"name": Optional(str)}, {}) == {}
assert validate({"name": str | None}, {"name": None}) == {"name": None}
assert validate({"name": Optional(str, "Ada")}, {}) == {"name": "Ada"}
# Released 0.8.0 defaults are inserted as supplied, without validation or copying.
default = []
result = validate({"items": Optional([str], default)}, {})
assert result["items"] is default
assert validate({"count": Optional(int, "unchecked")}, {})["count"] == "unchecked"
try:
    validate({"name": str | None}, {})
except ValueError:
    pass  # Nullable still requires the key.
else:
    raise AssertionError("Expected missing-key failure")
print("optional-defaults: passed")
