"""Structured error handling with ValidationError issue inspection."""

from zodify import ValidationError, validate


def main() -> None:
    print("=== Structured Error Inspection ===")
    schema = {"name": str, "age": int}
    data = {"name": 123, "age": "not_a_number", "extra": "key"}

    try:
        validate(schema, data, error_mode="structured")
    except ValidationError as error:
        print(f"Caught ValidationError with {len(error.issues)} issues:")
        for issue in sorted(error.issues, key=lambda item: item["path"]):
            print(f"  [{issue['path']}] {issue['message']}")
            print(f"    expected: {issue['expected']}, got: {issue['got']}")
    print()

    print("=== ValueError compatibility ===")
    try:
        validate({"x": int}, {"x": "bad"}, error_mode="structured")
    except ValueError as error:
        print(f"Caught as ValueError: {error}")
    print()


if __name__ == "__main__":
    main()

# Expected output:
# === Structured Error Inspection ===
# Caught ValidationError with 3 issues:
#   [age] expected int, got str
#     expected: int, got: str
#   [extra] unknown key
#     expected: known, got: unknown
#   [name] expected str, got int
#     expected: str, got: int
#
# === ValueError compatibility ===
# Caught as ValueError: x: expected int, got str
