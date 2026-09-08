import json
from zodify import validate

def read_user(text):
    data = json.loads(text)
    if type(data) is not dict:
        raise ValueError("Expected a JSON object")
    return validate({"name": str, "age": int}, data)

assert read_user('{"name":"Ada","age":36}')["age"] == 36
for invalid in ['[]', '{"name":"Ada","age":"36"}', '{"name":']:
    try:
        read_user(invalid)
    except ValueError:  # Includes JSONDecodeError.
        pass
    else:
        raise AssertionError("Expected parsing or validation failure")
print("json-object-validation: passed")
