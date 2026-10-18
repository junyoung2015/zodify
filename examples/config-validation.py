from zodify import Optional, validate

schema = {"host": str, "port": int, "debug": Optional(bool, False)}
config = {"host": "localhost", "port": 8080}
print(validate(schema, config))

with_typo = dict(config, debgu=True)
try:
    validate(schema, with_typo)
except ValueError as error:
    print(f"ValueError: {error}")

# Stripping drops the unknown field from the result.
print(validate(schema, with_typo, unknown_keys="strip"))
print("Original input:", with_typo)
