"""Flat union patterns including coercion priority and mismatch errors."""

from zodify import validate


def main() -> None:
    print("=== Success: basic union ===")
    print(validate({"value": str | int}, {"value": "hello"}))
    print(validate({"value": str | int}, {"value": 7}))
    print()

    print("=== Coercion priority: str | int vs int | str ===")
    raw = {"value": "42"}
    print(validate({"value": str | int}, raw, coerce=True))
    print(validate({"value": int | str}, raw, coerce=True))
    print()

    print("=== Error: union mismatch ===")
    try:
        validate({"value": str | int}, {"value": True})
    except ValueError as error:
        print(error)
    print()


if __name__ == "__main__":
    main()

# Expected output:
# === Success: basic union ===
# {'value': 'hello'}
# {'value': 7}
# 
# === Coercion priority: str | int vs int | str ===
# {'value': '42'}
# {'value': 42}
# 
# === Error: union mismatch ===
# value: expected str | int, got bool
