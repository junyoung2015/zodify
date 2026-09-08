import json
from zodify import validate

accepted = []
for token in ["1", "1.0", "true", '"1"']:
    value = json.loads(token)
    try:
        validate({"count": int}, {"count": value})
    except ValueError:
        accepted.append(False)
    else:
        accepted.append(True)
assert accepted == [True, False, False, False]
assert validate({"port": int}, {"port": "8080"}, coerce=True) == {"port": 8080}
assert validate({"value": int | str}, {"value": "1"}, coerce=True)["value"] == 1
assert validate({"value": str | int}, {"value": "1"}, coerce=True)["value"] == "1"
print("exact-types: passed")
