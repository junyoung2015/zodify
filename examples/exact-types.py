import json
from zodify import validate

for token in ["1", "1.0", "true", '"1"']:
    try:
        result = validate({"count": int}, {"count": json.loads(token)})
        print(f"{token}: {result}")
    except ValueError as error:
        print(f"{token}: {error}")

print(validate({"port": int}, {"port": "8080"}, coerce=True))
# Union order controls conversion of string inputs.
print(validate({"value": int | str}, {"value": "1"}, coerce=True))
print(validate({"value": str | int}, {"value": "1"}, coerce=True))
