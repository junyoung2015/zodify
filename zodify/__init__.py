"""zodify - Zod-inspired dict validation for Python."""

import os

__version__ = "0.0.1"
__all__ = ["__version__", "count_in_list", "validate", "env"]

_MISSING = object()
_BOOL_TRUE = {"true", "1", "yes"}
_BOOL_FALSE = {"false", "0", "no"}


def count_in_list(lst: list, item: any) -> int:
    """Count the number of occurrences of item in lst."""
    return lst.count(item)


def _coerce_value(value, target, key):
    """Coerce a value to the target type.

    Coercion to non-str targets only applies when value is a str.
    Any value can be coerced to str via str().

    Args:
        value: The value to coerce.
        target: The target type (str, int, float, bool).
        key: The key name for error messages.

    Returns:
        The coerced value.

    Raises:
        ValueError: If coercion fails.
    """
    if target is str:
        return str(value)
    if type(value) is not str:
        raise ValueError(
            f"{key}: expected {target.__name__}, "
            f"got {type(value).__name__}"
        )
    if not value:
        raise ValueError(
            f"{key}: cannot coerce empty string to "
            f"{target.__name__}"
        )
    if target is bool:
        lower = value.lower()
        if lower in _BOOL_TRUE:
            return True
        if lower in _BOOL_FALSE:
            return False
        raise ValueError(
            f"{key}: cannot coerce '{value}' to bool"
        )
    if target is int:
        try:
            return int(value)
        except (ValueError, TypeError):
            raise ValueError(
                f"{key}: cannot coerce '{value}' to int"
            )
    if target is float:
        try:
            return float(value)
        except (ValueError, TypeError):
            raise ValueError(
                f"{key}: cannot coerce '{value}' to float"
            )
    raise ValueError(
        f"{key}: cannot coerce to {target.__name__}"
    )


def validate(schema: dict, data: dict,
             coerce: bool = False) -> dict:
    """Validate a dict against a type schema.

    Args:
        schema: Dict mapping keys to expected types
                (str, int, float, bool, list, dict).
        data: The dict to validate.
        coerce: If True, attempt to cast string values to the
                target type. Coercion ONLY applies to str inputs.

    Returns:
        A new dict containing only the schema-declared keys
        with their (possibly coerced) values. Extra keys in
        data are stripped.

    Raises:
        TypeError: If schema or data is not a dict.
        ValueError: If any key fails validation. Message
                    contains ALL errors separated by newlines.
    """
    if type(schema) is not dict:
        raise TypeError("schema must be a dict")
    if type(data) is not dict:
        raise TypeError("data must be a dict")
    errors = []
    result = {}
    for key, expected in schema.items():
        if key not in data:
            errors.append(f"{key}: missing required key")
            continue
        value = data[key]
        if type(value) is expected:
            result[key] = value
        elif coerce:
            try:
                result[key] = _coerce_value(
                    value, expected, key
                )
            except ValueError as e:
                errors.append(str(e))
        else:
            errors.append(
                f"{key}: expected {expected.__name__}, "
                f"got {type(value).__name__}"
            )
    if errors:
        raise ValueError("\n".join(errors))
    return result


def env(name: str, cast: type, default=_MISSING):
    """Read and type-cast an environment variable.

    Args:
        name: The environment variable name.
        cast: Target type (str, int, float, bool).
        default: Default value if env var is not set.
                 If not provided, missing vars raise
                 ValueError. Defaults are NOT type-checked.

    Returns:
        The typed value of the environment variable.

    Raises:
        ValueError: If the env var is missing (with no
                    default) or cannot be cast to the
                    target type.
    """
    value = os.environ.get(name)
    if value is None:
        if default is not _MISSING:
            return default
        raise ValueError(
            f"{name}: missing required env var"
        )
    return _coerce_value(value, cast, name)


def main():
    """Entry point for zodify module."""
    pass


if __name__ == "__main__":
    main()
