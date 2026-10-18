from zodify import Schema, validate

class User(Schema):
    name: str
    age: int

user = validate(User, {"name": "Ada", "age": 36})
print(user.name)
print(user.age)
