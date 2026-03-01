"""zodify - Zod-inspired dict validation for Python."""

import os
from typing import Any, Literal, TypeVar, cast as typing_cast, overload

__version__: str = "0.2.1"
__all__ = ["__version__", "validate", "env", "Optional"]

_MISSING: object = object()
_BOOL_TRUE = {"true", "1", "yes"}
_BOOL_FALSE = {"false", "0", "no"}
UnknownKeysMode = Literal["reject", "strip"]
_DictValueT = TypeVar("_DictValueT")
_SchemaValueT = TypeVar("_SchemaValueT")
_EnvCastT = TypeVar("_EnvCastT", str, int, float, bool)


class Optional:
    """Mark a schema key as optional with an optional default

    Args:
        type: The expected type for the value when present.
        default: Default value if key is absent from data.
                 If omitted, absent keys are excluded from
                 the result.

    Example:
        >>> from zodify import validate, Optional
        >>> schema = {"name": str, "role": Optional(str, "user")}
        >>> validate(schema, {"name": "Alice"})
        {'name': 'Alice', 'role': 'user'}
    """

    type: Any
    default: Any
    __slots__ = ("type", "default")

    def __init__(self, type: Any, default: Any = _MISSING) -> None:
        self.type = type
        self.default = default

    def __repr__(self) -> str:
        if self.default is _MISSING:
            return f"Optional({self.type!r})"
        return f"Optional({self.type!r}, {self.default!r})"


def _coerce_value(value: Any, target: type, key: str) -> Any:
    """Coerce a value to the target type"""
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


def _check_value(value: Any, expected: Any, key: str, coerce: bool,
                 errors: list[tuple[str, str, str, str]], depth: int,
                 unknown_keys: UnknownKeysMode) -> Any:
    """Validate one value against one schema entry"""
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
            except ValueError:
                if type(value) is not str:
                    msg = f"expected {expected.__name__}, got {type(value).__name__}"
                elif not value:
                    msg = f"cannot coerce empty string to {expected.__name__}"
                else:
                    msg = f"cannot coerce '{value}' to {expected.__name__}"
                errors.append((key, msg, expected.__name__,
                               type(value).__name__))
                return _MISSING
        errors.append((
            key, f"expected {expected.__name__}, got {type(value).__name__}",
            expected.__name__, type(value).__name__))
        return _MISSING
    if callable(expected):
        try:
            if expected(value):
                return value
        except Exception as exc:
            errors.append((
                key,
                f"custom validation failed ({type(exc).__name__}: {exc})",
                "callable",
                "failed",
            ))
            return _MISSING
        errors.append((key, "custom validation failed", "callable", "failed"))
        return _MISSING
    raise TypeError(
        f"invalid schema value for key '{key}': "
        f"{expected!r}"
    )


def _validate(schema: dict[str, Any], data: dict[str, Any], coerce: bool,
              prefix: str, errors: list[tuple[str, str, str, str]], depth: int,
              unknown_keys: UnknownKeysMode) -> dict[str, Any]:
    """Iterate schema keys and validate each value"""
    result: dict[str, Any] = {}
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


@overload
def validate(
    schema: dict[str, type[_SchemaValueT]],
    data: dict[str, Any],
    *,
    coerce: bool = False,
    max_depth: int = 32,
    unknown_keys: Literal["reject"] = "reject",
) -> dict[str, _SchemaValueT]:
    ...


@overload
def validate(
    schema: dict[str, Any],
    data: dict[str, _DictValueT],
    *,
    coerce: bool = False,
    max_depth: int = 32,
    unknown_keys: Literal["reject"] = "reject",
) -> dict[str, _DictValueT]:
    ...


@overload
def validate(
    schema: dict[str, Any],
    data: dict[str, Any],
    *,
    coerce: bool = False,
    max_depth: int = 32,
    unknown_keys: Literal["strip"],
) -> dict[str, Any]:
    ...


def validate(schema: dict[str, Any], data: dict[str, Any], *, coerce: bool = False,
             max_depth: int = 32, unknown_keys: UnknownKeysMode = "reject") -> dict[str, Any]:
    """Validate a dict against a type schema

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
        TypeError: If schema or data is not a dict, or
                   if schema contains invalid values.
        ValueError: If any key fails validation or
                    unknown_keys is not "reject" or "strip".

    Example:
        >>> from zodify import validate
        >>> validate({"name": str, "age": int}, {"name": "Alice", "age": 30})
        {'name': 'Alice', 'age': 30}
    """
    if type(schema) is not dict:
        raise TypeError("schema must be a dict")
    if type(data) is not dict:
        raise TypeError("data must be a dict")
    if unknown_keys not in ("reject", "strip"):
        raise ValueError("unknown_keys must be 'reject' or 'strip'")
    errors: list[tuple[str, str, str, str]] = []
    result = _validate(
        schema, data, coerce, "", errors, max_depth,
        unknown_keys,
    )
    if errors:
        raise ValueError("\n".join(
            f"{path}: {msg}" for path, msg, _, _ in errors
        ))
    return result


@overload
def env(name: str, cast: type[_EnvCastT]) -> _EnvCastT:
    ...


@overload
def env(name: str, cast: type[_EnvCastT], default: _EnvCastT) -> _EnvCastT:
    ...


def env(name: str, cast: type[_EnvCastT], default: object = _MISSING) -> _EnvCastT:
    """Read and type-cast an environment variable

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

    Example:
        >>> import os; os.environ["PORT"] = "8080"
        >>> from zodify import env
        >>> env("PORT", int)
        8080
        >>> del os.environ["PORT"]
    """
    value = os.environ.get(name)
    if value is None:
        if default is not _MISSING:
            return typing_cast(_EnvCastT, default)
        raise ValueError(
            f"{name}: missing required env var"
        )
    return typing_cast(_EnvCastT, _coerce_value(value, cast, name))
