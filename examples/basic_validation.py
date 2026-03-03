"""Flat dict validation success and common text-mode errors."""

from zodify import validate


def main() -> None:
    print("=== Success: flat validation ===")
    schema = {"name": str, "age": int}
    data = {"name": "Alice", "age": 30}
    result = validate(schema, data)
    print(result)
    print()

    print("=== Error: type mismatch ===")
    try:
        validate(schema, {"name": "Alice", "age": "thirty"})
    except ValueError as error:
        print(error)
    print()

    print("=== Error: missing key ===")
    try:
        validate(schema, {"name": "Alice"})
    except ValueError as error:
        print(error)
    print()


if __name__ == "__main__":
    main()

# Expected output:
# === Success: flat validation ===
# {'name': 'Alice', 'age': 30}
# 
# === Error: type mismatch ===
# age: expected int, got str
# 
# === Error: missing key ===
# age: missing required key
