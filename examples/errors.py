from zodify import ValidationError, validate

try:
    validate({"port": int}, {"port": "wrong"}, error_mode="structured")
except ValidationError as error:
    print(error.issues[0])
