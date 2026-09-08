from zodify import Schema, validate

class User(Schema):
    name: str
    age: int

user = validate(User, {"name": "Ada", "age": 36})
assert user.name == "Ada"
assert user.age == 36
print("class-schemas: passed")
