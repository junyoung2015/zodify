from zodify import validate

schema = {"users": [{"name": str}], "enabled": bool}
assert validate(schema, {"users": [{"name": "Ada"}], "enabled": True})["users"][0]["name"] == "Ada"
# A predicate accepts the original value when it returns a truthy result.
assert validate({"port": lambda x: type(x) is int and 1 <= x <= 65535}, {"port": 8080}) == {"port": 8080}
print("schemas: passed")
