import json
from zodify import validate

def read_user(text):
    data = json.loads(text)
    if type(data) is not dict:
        raise ValueError("Expected a JSON object")
    return validate({"name": str, "age": int}, data)

print(read_user('{"name":"Ada","age":36}'))
for text in ['[]', '{"name":"Ada","age":"36"}', '{"name":']:
    try:
        read_user(text)
    except json.JSONDecodeError as error:
        print(f"JSONDecodeError: {error.msg}")
    except ValueError as error:
        print(f"ValueError: {error}")
