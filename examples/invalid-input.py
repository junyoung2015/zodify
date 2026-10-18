from zodify import validate

try:
    validate({"port": int}, {"port": "8080"})
except ValueError as error:
    print(f"ValueError: {error}")
