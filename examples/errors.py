from zodify import ValidationError, validate

try:
    validate({"port": int}, {"port": "wrong"}, error_mode="structured")
except ValidationError as error:
    assert error.issues[0]["path"] == "port"
    assert error.issues[0]["expected"] == "int"
else:
    raise AssertionError("Expected structured failure")
print("errors: passed")
