from zodify import validate

schema = {"port": int, "debug": bool}
data = {"port": 8080, "debug": False}

print(validate(schema, data))
