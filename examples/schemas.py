from zodify import validate

schema = {"users": [{"name": str}], "enabled": bool}
data = {"users": [{"name": "Ada"}], "enabled": True}
print(validate(schema, data))

# A truthy predicate accepts and preserves the original value.
port_schema = {"port": lambda value: type(value) is int and 1 <= value <= 65535}
print(validate(port_schema, {"port": 8080}))
