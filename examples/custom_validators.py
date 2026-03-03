"""Callable validator examples with lambda and named function behavior."""

from zodify import validate


def even_number(value: object) -> bool:
    return isinstance(value, int) and value % 2 == 0


def looks_like_email(value: object) -> bool:
    return isinstance(value, str) and "@" in value


def validator_raises(_value: object) -> bool:
    raise ValueError("validator exploded")


def main() -> None:
    print("=== Success: lambda validator ===")
    print(validate({"nickname": lambda value: isinstance(value, str) and len(value) >= 3}, {"nickname": "ally"}))
    print()

    print("=== Error: lambda validator returned False ===")
    try:
        validate({"nickname": lambda value: isinstance(value, str) and len(value) >= 3}, {"nickname": "xy"})
    except ValueError as error:
        print(error)
    print()

    print("=== Success: named function validators ===")
    schema = {"count": even_number, "email": looks_like_email}
    print(validate(schema, {"count": 4, "email": "alice@example.com"}))
    print()

    print("=== Error: named validator returned False ===")
    try:
        validate(schema, {"count": 3, "email": "alice@example.com"})
    except ValueError as error:
        print(error)
    print()

    print("=== Error: validator raised ===")
    try:
        validate({"email": validator_raises}, {"email": "alice@example.com"})
    except ValueError as error:
        print(error)
    print()


if __name__ == "__main__":
    main()

# Expected output:
# === Success: lambda validator ===
# {'nickname': 'ally'}
# 
# === Error: lambda validator returned False ===
# nickname: custom validation failed
# 
# === Success: named function validators ===
# {'count': 4, 'email': 'alice@example.com'}
# 
# === Error: named validator returned False ===
# count: custom validation failed
# 
# === Error: validator raised ===
# email: custom validation failed (ValueError: validator exploded)
