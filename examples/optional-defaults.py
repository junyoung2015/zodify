from zodify import Optional, validate

print(validate({"name": Optional(str)}, {}))
print(validate({"name": str | None}, {"name": None}))
print(validate({"name": Optional(str, "Ada")}, {}))

# Defaults are trusted: neither copied nor validated.
default = []
result = validate({"items": Optional([str], default)}, {})
print("Shares default:", result["items"] is default)
print(validate({"count": Optional(int, "unchecked")}, {}))

try:
    validate({"name": str | None}, {})
except ValueError as error:
    print(f"ValueError: {error}")
