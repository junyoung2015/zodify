"""zodify - Zod-inspired dict validation for Python."""

import os

__version__ = "0.2.0"
__all__ = ["__version__", "validate", "env", "Optional"]

_MISSING = object()
_BOOL_TRUE = {"true", "1", "yes"}
_BOOL_FALSE = {"false", "0", "no"}


class Optional:
    """Marker for optional schema keys with an optional default."""

    __slots__ = ("type", "default")

    def __init__(self, type, default=_MISSING):
        self.type = type
        self.default = default

    def __repr__(self):
        if self.default is _MISSING:
            return f"Optional({self.type!r})"
        return f"Optional({self.type!r}, {self.default!r})"


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
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"{key}: cannot coerce '{value}' to int"
            ) from e
    if target is float:
        try:
            return float(value)
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"{key}: cannot coerce '{value}' to float"
            ) from e
    raise ValueError(
        f"{key}: cannot coerce to {target.__name__}"
    )


def _check_value(value, expected, key, coerce, errors, depth,
                 unknown_keys):
    """Validate one value against one schema entry.

    Returns validated value on success, _MISSING on direct
    failure (appending to shared errors list).
    Passes unknown_keys through to nested _validate and
    recursive _check_value calls.
    """
    if isinstance(expected, dict):
        if type(value) is not dict:
            errors.append((key, f"expected dict, got {type(value).__name__}",
                           "dict", type(value).__name__))
            return _MISSING
        return _validate(expected, value, coerce,
                         key + ".", errors, depth - 1, unknown_keys)
    if isinstance(expected, list) and len(expected) == 1:
        if type(value) is not list:
            errors.append((key, f"expected list, got {type(value).__name__}",
                           "list", type(value).__name__))
            return _MISSING
        result = []
        for i, item in enumerate(value):
            checked = _check_value(item, expected[0], f"{key}[{i}]",
                                   coerce, errors, depth, unknown_keys)
            if checked is not _MISSING:
                result.append(checked)
        return result
    if isinstance(expected, list):
        raise TypeError(
            f"invalid schema value for key '{key}': "
            f"list schema must contain exactly one "
            f"element type, got {len(expected)}"
        )
    if type(expected) is type:
        if type(value) is expected:
            return value
        if coerce:
            try:
                return _coerce_value(value, expected, key)
            except ValueError as e:
                msg = str(e).removeprefix(f"{key}: ")
                errors.append((key, msg, expected.__name__,
                               type(value).__name__))
                return _MISSING
        errors.append((
            key, f"expected {expected.__name__}, got {type(value).__name__}",
            expected.__name__, type(value).__name__))
        return _MISSING
    if callable(expected):
        try:
            if expected(value): return value
        except Exception: pass
        errors.append((key, "custom validation failed", "callable", "failed"))
        return _MISSING
    raise TypeError(
        f"invalid schema value for key '{key}': "
        f"{expected!r}"
    )


def _validate(schema, data, coerce, prefix, errors, depth,
              unknown_keys):
    """Iterate schema keys, handle Optional/missing, delegate
    to _check_value. Returns result dict only.
    If depth <= 0, appends a depth-exceeded error and returns
    immediately.
    Checks for unknown keys in data when unknown_keys="reject"."""
    result = {}
    if depth <= 0:
        errors.append((prefix.rstrip("."),
                       "max depth exceeded",
                       "max_depth", "exceeded"))
        return result
    for key, expected in schema.items():
        if isinstance(expected, Optional):
            exp = expected.type
            default = expected.default
        else:
            exp = expected
            default = _MISSING
        full_key = f"{prefix}{key}"
        if key not in data:
            if default is not _MISSING:
                result[key] = default
            elif isinstance(expected, Optional):
                pass  # no default, key absent from result
            else:
                errors.append((
                    full_key, "missing required key",
                    "required", "missing",
                ))
            continue
        checked = _check_value(
            data[key], exp, full_key, coerce, errors, depth,
            unknown_keys,
        )
        if checked is not _MISSING:
            result[key] = checked
    if unknown_keys == "reject":
        for key in data:
            if key not in schema:
                errors.append((f"{prefix}{key}", "unknown key",
                               "known", "unknown"))
    return result


def validate(schema, data, *, coerce=False, max_depth=32,
             unknown_keys="reject"):
    """Validate a dict against a type schema.

    Args:
        schema: Dict mapping keys to expected types.
        data: The dict to validate.
        coerce: If True, cast string values to target types.
        max_depth: Maximum nesting depth (default 32).
        unknown_keys: How to handle extra keys ("reject" or
                      "strip"). Default "reject".

    Returns:
        A new dict with only schema-declared keys.

    Raises:
        TypeError: If schema or data is not a dict.
        ValueError: If any key fails validation.
    """
    if type(schema) is not dict:
        raise TypeError("schema must be a dict")
    if type(data) is not dict:
        raise TypeError("data must be a dict")
    if unknown_keys not in ("reject", "strip"):
        raise ValueError("unknown_keys must be 'reject' or 'strip'")
    errors = []
    result = _validate(
        schema, data, coerce, "", errors, max_depth,
        unknown_keys,
    )
    if errors:
        raise ValueError("\n".join(
            f"{path}: {msg}" for path, msg, _, _ in errors
        ))
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
