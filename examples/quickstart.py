from zodify import validate

schema = {"name": str, "age": int}
print(validate(schema, {"name": "Ada", "age": 36}))

try:
    validate(schema, {"name": "Ada", "age": "36"})
except ValueError as error:
    print(f"ValueError: {error}")
