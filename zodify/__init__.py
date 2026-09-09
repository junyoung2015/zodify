"""zodify - Validation for Python dictionaries with no required runtime dependencies."""

import os
import types
from typing import Any, Literal, TypeVar, cast as typing_cast, overload

from ._issues import ValidationIssue, _IssueList, _Location, _child_loc, _record_issue

__version__: str = "0.8.0"
__all__ = ["__version__", "validate", "env", "load_env", "Validator", "Optional", "ValidationError", "ValidationIssue", "Schema", "to_json_schema"]

_MISSING: object = object()
_BOOL_TRUE = {"true", "1", "yes"}
_BOOL_FALSE = {"false", "0", "no"}
UnknownKeysMode = Literal["reject", "strip"]
ErrorMode = Literal["text", "structured"]
OnMissingMode = Literal["raise", "empty"]
_SchemaT = TypeVar("_SchemaT", bound="Schema")
_DictValueT = TypeVar("_DictValueT")
_SchemaValueT = TypeVar("_SchemaValueT")
_EnvCastT = TypeVar("_EnvCastT", str, int, float, bool)


class ValidationError(ValueError):
    """Validation error with legacy issues and optional canonical diagnostics.

    Engine failures expose an immutable ``details`` tuple of ValidationIssue
    records. Manual construction and .env parser failures have ``details=None``.
    Unsupported runtime key types also have no canonical snapshot: keys must
    be exact str/int to form a lossless typed location. Legacy issues remain
    independently mutable. Detail messages omit raw input and callback error
    text; locations and type names can still contain sensitive information.

    Args:
        issues: List of issue dicts, each with keys
                ``path``, ``message``, ``expected``, ``got``.
                Dicts must contain at least ``path`` and
                ``message``; a ``KeyError`` is raised otherwise.

    Example:
        >>> from zodify import ValidationError
        >>> e = ValidationError([{"path": "db.port", "message": "expected int, got str", "expected": "int", "got": "str"}])
        >>> str(e)
        'db.port: expected int, got str'
    """

    # Legacy records remain independently mutable; no path-string reparsing.
    issues: list[dict[str, str]]
    details: tuple[ValidationIssue, ...] | None
    __slots__ = ("issues", "details")

    def __init__(self, issues: list[dict[str, str]]) -> None:
        self.issues = [dict(d) for d in issues]
        self.details = None
        super().__init__("\n".join(
            f"{d['path']}: {d['message']}" for d in self.issues
        ))

    def __reduce__(self) -> tuple[object, tuple[list[dict[str, str]]], dict[str, object]]:
        # Reconstruct through the legacy constructor, then restore the snapshot.
        return (self.__class__, (self.issues,), {"details": self.details})


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


def _resolve_mode_options(
    unknown_keys: object,
    error_mode: object,
) -> tuple[UnknownKeysMode, ErrorMode]:
    """Validate and normalize unknown_keys/error_mode options."""
    if unknown_keys not in ("reject", "strip"):
        raise ValueError("unknown_keys must be 'reject' or 'strip'")
    if error_mode not in ("text", "structured"):
        raise ValueError("error_mode must be 'text' or 'structured'")
    return (
        unknown_keys,
        error_mode,
    )


def _raise_validation_issues(
    errors: list[tuple[str, str, str, str]],
    error_mode: ErrorMode,
) -> None:
    if error_mode == "structured":
        error = ValidationError([{"path": p, "message": m, "expected": e, "got": g} for p, m, e, g in errors])
        if isinstance(errors, _IssueList) and errors.details is not None:
            error.details = tuple(errors.details)
        raise error
    raise ValueError("\n".join(f"{path}: {msg}" for path, msg, _, _ in errors))


def _check_list(value: Any, expected: list[Any], key: str, coerce: bool,
                errors: list[tuple[str, str, str, str]], depth: int,
                unknown_keys: UnknownKeysMode, loc: _Location = None) -> Any:
    """Validate each element in a list against the expected type"""
    if type(value) is not list:
        _record_issue(errors, loc, "type_mismatch", (key, f"expected list, got {type(value).__name__}",
                       "list", type(value).__name__))
        return _MISSING
    result: list[Any] = []
    for i, item in enumerate(value):
        checked = _check_value(item, expected[0], f"{key}[{i}]",
                               coerce, errors, depth, unknown_keys, _child_loc(loc, i) if loc is not None else None)
        if checked is not _MISSING:
            result.append(checked)
    return result


def _check_type(value: Any, expected: type, key: str, coerce: bool,
                errors: list[tuple[str, str, str, str]], loc: _Location = None) -> Any:
    """Check a value against an expected type with optional coercion"""
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
            _record_issue(errors, loc, "coercion_failed", (key, msg, expected.__name__,
                           type(value).__name__))
            return _MISSING
    _record_issue(errors, loc, "type_mismatch", (
        key, f"expected {expected.__name__}, got {type(value).__name__}",
        expected.__name__, type(value).__name__))
    return _MISSING


def _check_value(value: Any, expected: Any, key: str, coerce: bool,
                 errors: list[tuple[str, str, str, str]], depth: int,
                 unknown_keys: UnknownKeysMode, loc: _Location = None) -> Any:
    """Validate one value against one schema entry"""
    if isinstance(expected, dict):
        if type(value) is not dict:
            _record_issue(errors, loc, "type_mismatch", (key, f"expected dict, got {type(value).__name__}",
                           "dict", type(value).__name__))
            return _MISSING
        return _validate(expected, value, coerce,
                         key + ".", errors, depth - 1, unknown_keys, loc)
    if isinstance(expected, list) and len(expected) == 1:
        return _check_list(value, expected, key, coerce, errors, depth, unknown_keys, loc)
    if isinstance(expected, list):
        raise TypeError(
            f"invalid schema value for key '{key}': "
            f"list schema must contain exactly one "
            f"element type, got {len(expected)}"
        )
    if isinstance(expected, types.UnionType):
        for t in expected.__args__:
            if type(value) is t and (not coerce or t is not str):
                return value
        if coerce:
            for t in expected.__args__:
                try:
                    return _coerce_value(value, t, key)
                except ValueError:
                    pass
        type_names = " | ".join(t.__name__ for t in expected.__args__)
        _record_issue(errors, loc, "union_mismatch", (key, f"expected {type_names}, got {type(value).__name__}",
                       type_names, type(value).__name__))
        return _MISSING
    if type(expected) is type:
        return _check_type(value, expected, key, coerce, errors, loc)
    if callable(expected):
        try:
            if expected(value):
                return value
        except Exception as exc:
            _record_issue(errors, loc, "custom_validation_failed", (
                key,
                f"custom validation failed ({type(exc).__name__}: {exc})",
                "callable",
                "failed",
            ))
            return _MISSING
        _record_issue(errors, loc, "custom_validation_failed", (key, "custom validation failed", "callable", "failed"))
        return _MISSING
    raise TypeError(
        f"invalid schema value for key '{key}': "
        f"{expected!r}"
    )


def _validate(schema: dict[str, Any], data: dict[str, Any], coerce: bool,
              prefix: str, errors: list[tuple[str, str, str, str]], depth: int,
              unknown_keys: UnknownKeysMode, loc: _Location = None) -> dict[str, Any]:
    """Iterate schema keys and validate each value"""
    result: dict[str, Any] = {}
    if depth <= 0:
        _record_issue(errors, loc, "depth_exceeded", (prefix.rstrip("."),
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
                _record_issue(errors, _child_loc(loc, key) if loc is not None else None, "missing_key", (
                    full_key, "missing required key",
                    "required", "missing",
                ))
            continue
        checked = _check_value(
            data[key], exp, full_key, coerce, errors, depth,
            unknown_keys, _child_loc(loc, key) if loc is not None else None,
        )
        if checked is not _MISSING:
            result[key] = checked
    if unknown_keys == "reject":
        for key in data:
            if key not in schema:
                _record_issue(errors, _child_loc(loc, key) if loc is not None else None, "unknown_key", (f"{prefix}{key}", "unknown key",
                               "known", "unknown"))
    return result


@overload
def validate(
    schema: type[_SchemaT],
    data: dict[str, Any],
    *,
    coerce: bool = False,
    max_depth: int = 32,
    unknown_keys: UnknownKeysMode = "reject",
    error_mode: ErrorMode = "text",
) -> _SchemaT:
    ...


@overload
def validate(
    schema: dict[str, type[_SchemaValueT]],
    data: dict[str, Any],
    *,
    coerce: bool = False,
    max_depth: int = 32,
    unknown_keys: Literal["reject"] = "reject",
    error_mode: ErrorMode = "text",
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
    error_mode: ErrorMode = "text",
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
    error_mode: ErrorMode = "text",
) -> dict[str, Any]:
    ...


def validate(
    schema: type[_SchemaT] | dict[str, Any],
    data: dict[str, Any],
    *,
    coerce: bool = False,
    max_depth: int = 32,
    unknown_keys: UnknownKeysMode = "reject",
    error_mode: ErrorMode = "text",
) -> _SchemaT | dict[str, Any]:
    """Validate a dict against a plain schema dict or Schema subclass

    Args:
        schema: Dict mapping keys to expected types, or a
                `Schema` subclass compiled into an equivalent
                plain dict schema.
        data: The dict to validate.
        coerce: If True, cast string values to target types.
        max_depth: Maximum dictionary depth (default 32). Root is depth
                   one; list wrappers consume no additional depth. Bare dict
                   and list type checks do not traverse their contents.
        unknown_keys: How to handle extra keys ("reject" or
                      "strip"). Default "reject".
        error_mode: Error output format. ``"text"`` raises
                    ``ValueError`` with human-readable strings
                    (default). ``"structured"`` raises
                    ``ValidationError`` with ``.issues`` list
                    of dicts and a canonical ``.details`` snapshot.

    Returns:
        A new plain dict for dict-schema input, or a dict-
        compatible wrapped Schema result for Schema input.

    Raises:
        TypeError: If schema or data is not valid input, or if
                   schema contains invalid values.
        ValueError: If any key fails validation (text mode),
                    or if unknown_keys / error_mode is invalid.
        ValidationError: If any key fails validation
                         (structured mode). Subclass of
                         ValueError.

    Example:
        >>> from zodify import validate
        >>> validate({"name": str, "age": int}, {"name": "Alice", "age": 30})
        {'name': 'Alice', 'age': 30}
    """
    normalized_schema, schema_type = normalize_schema_input(schema)
    if type(data) is not dict:
        raise TypeError("data must be a dict")
    resolved_unknown_keys, resolved_error_mode = _resolve_mode_options(
        unknown_keys,
        error_mode,
    )
    errors: list[tuple[str, str, str, str]] = _IssueList() if resolved_error_mode == "structured" else []
    result = _validate(
        normalized_schema, data, coerce, "", errors, max_depth,
        resolved_unknown_keys, () if resolved_error_mode == "structured" else None,
    )
    if errors: _raise_validation_issues(errors, resolved_error_mode)
    if schema_type is None:
        return result
    return wrap_schema_result(schema_type, result)


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


@overload
def load_env(
    path: str | os.PathLike[str] = ".env",
    *,
    error_mode: ErrorMode = "text",
    on_missing: OnMissingMode = "raise",
) -> dict[str, str]:
    ...


@overload
def load_env(
    path: str | os.PathLike[str] = ".env",
    *,
    schema: dict[str, type[_SchemaValueT]],
    coerce: bool = True,
    max_depth: int = 32,
    unknown_keys: Literal["strip", "reject"] = "strip",
    error_mode: ErrorMode = "text",
    on_missing: OnMissingMode = "raise",
) -> dict[str, _SchemaValueT]:
    ...


@overload
def load_env(
    path: str | os.PathLike[str] = ".env",
    *,
    schema: dict[str, Any],
    coerce: bool = True,
    max_depth: int = 32,
    unknown_keys: Literal["strip", "reject"] = "strip",
    error_mode: ErrorMode = "text",
    on_missing: OnMissingMode = "raise",
) -> dict[str, Any]:
    ...


@overload
def load_env(
    path: str | os.PathLike[str] = ".env",
    *,
    schema: type[_SchemaT],
    coerce: bool = True,
    max_depth: int = 32,
    unknown_keys: Literal["strip", "reject"] = "strip",
    error_mode: ErrorMode = "text",
    on_missing: OnMissingMode = "raise",
) -> _SchemaT:
    ...


def load_env(
    path: str | os.PathLike[str] = ".env",
    *,
    schema: object = _MISSING,
    coerce: object = _MISSING,
    max_depth: object = _MISSING,
    unknown_keys: object = _MISSING,
    error_mode: ErrorMode = "text",
    on_missing: OnMissingMode = "raise",
) -> Any:
    """Load and optionally validate a .env file

    Args:
        path: The .env file path. Relative paths resolve from
              the current working directory.
        schema: Optional dict schema or Schema subclass for
                validation.
        coerce: Schema-mode override for string coercion.
                Defaults to True in schema mode.
        max_depth: Schema-mode override for nested validation
                   depth. Defaults to 32 in schema mode.
        unknown_keys: Schema-mode override for extra keys.
                      Defaults to "strip" in schema mode.
        error_mode: Error output format. ``"text"`` raises
                    ``ValueError`` / ``FileNotFoundError``.
                    ``"structured"`` raises
                    ``ValidationError`` for parser failures.
        on_missing: Missing-file behavior. ``"raise"`` raises
                    an error; ``"empty"`` validates an empty
                    mapping instead.

    Returns:
        A raw ``dict[str, str]`` when no schema is supplied,
        or the existing validate() result for schema mode.

    Raises:
        TypeError: If schema-only kwargs are supplied without
                   ``schema``.
        ValueError: If parser or validation checks fail in
                    text mode, or if on_missing is invalid.
        FileNotFoundError: If the file is missing in text
                           mode and ``on_missing="raise"``.
        ValidationError: If parser checks fail in structured
                         mode.

    Example:
        >>> import os, tempfile
        >>> from pathlib import Path
        >>> from zodify import load_env
        >>> with tempfile.TemporaryDirectory() as tmp:
        ...     path = Path(tmp) / ".env"
        ...     _ = path.write_text("PORT=8080\\n", encoding="utf-8")
        ...     load_env(path, schema={"PORT": int})
        {'PORT': 8080}
    """
    if schema is _MISSING and (coerce is not _MISSING or max_depth is not _MISSING or unknown_keys is not _MISSING):
        raise TypeError("schema is required when using coerce, max_depth, or unknown_keys")
    if on_missing not in ("raise", "empty"): raise ValueError("on_missing must be 'raise' or 'empty'")
    resolved_path = _envfile.resolve_env_path(path)
    resolved_unknown_keys, resolved_error_mode = _resolve_mode_options(("reject" if schema is _MISSING else "strip") if unknown_keys is _MISSING else unknown_keys, error_mode)
    try: data, errors = _envfile.parse_env_file(resolved_path)
    except FileNotFoundError:
        if on_missing == "empty": data, errors = {}, []
        elif resolved_error_mode == "structured":
            raise ValidationError([{"path": f"{resolved_path}[missing]", "message": "file not found", "expected": "existing .env file", "got": "missing path"}]) from None
        else: raise
    if errors: _raise_validation_issues(errors, resolved_error_mode)
    if schema is _MISSING: return data
    return validate(
        typing_cast(Any, schema),
        data,
        coerce=typing_cast(bool, True if coerce is _MISSING else coerce),
        max_depth=typing_cast(int, 32 if max_depth is _MISSING else max_depth),
        unknown_keys=resolved_unknown_keys,
        error_mode=resolved_error_mode,
    )


class Validator:
    """Validate dict or Schema data with reusable default validate() options

    Args:
        coerce: Default value for ``validate(..., coerce=...)``.
        max_depth: Default value for ``validate(..., max_depth=...)``.
        unknown_keys: Default value for ``validate(..., unknown_keys=...)``.
        error_mode: Default value for ``validate(..., error_mode=...)``.

    Example:
        >>> from zodify import Validator
        >>> v = Validator(coerce=True, error_mode="structured")
        >>> v.validate({"port": int}, {"port": "8080"})
        {'port': 8080}
    """

    __slots__ = ("coerce", "max_depth", "unknown_keys", "error_mode")

    coerce: bool
    max_depth: int
    unknown_keys: UnknownKeysMode
    error_mode: ErrorMode

    def __init__(
        self,
        *,
        coerce: bool = False,
        max_depth: int = 32,
        unknown_keys: UnknownKeysMode = "reject",
        error_mode: ErrorMode = "text",
    ) -> None:
        resolved_unknown_keys, resolved_error_mode = _resolve_mode_options(
            unknown_keys,
            error_mode,
        )
        self.coerce = coerce
        self.max_depth = max_depth
        self.unknown_keys = resolved_unknown_keys
        self.error_mode = resolved_error_mode

    @overload
    def validate(
        self,
        schema: type[_SchemaT],
        data: dict[str, Any],
        *,
        coerce: bool = ...,
        max_depth: int = ...,
        unknown_keys: UnknownKeysMode = ...,
        error_mode: ErrorMode = ...,
    ) -> _SchemaT:
        ...

    @overload
    def validate(
        self,
        schema: dict[str, type[_SchemaValueT]],
        data: dict[str, Any],
        *,
        coerce: bool = ...,
        max_depth: int = ...,
        unknown_keys: Literal["reject"] = ...,
        error_mode: ErrorMode = ...,
    ) -> dict[str, _SchemaValueT]:
        ...

    @overload
    def validate(
        self,
        schema: dict[str, Any],
        data: dict[str, _DictValueT],
        *,
        coerce: bool = ...,
        max_depth: int = ...,
        unknown_keys: Literal["reject"] = ...,
        error_mode: ErrorMode = ...,
    ) -> dict[str, _DictValueT]:
        ...

    @overload
    def validate(
        self,
        schema: dict[str, Any],
        data: dict[str, Any],
        *,
        coerce: bool = ...,
        max_depth: int = ...,
        unknown_keys: Literal["strip"],
        error_mode: ErrorMode = ...,
    ) -> dict[str, Any]:
        ...

    def validate(
        self,
        schema: type[_SchemaT] | dict[str, Any],
        data: dict[str, Any],
        *,
        coerce: object = _MISSING,
        max_depth: object = _MISSING,
        unknown_keys: object = _MISSING,
        error_mode: object = _MISSING,
    ) -> _SchemaT | dict[str, Any]:
        use_coerce = self.coerce if coerce is _MISSING else coerce
        use_max_depth = self.max_depth if max_depth is _MISSING else max_depth
        use_unknown_keys = (
            self.unknown_keys
            if unknown_keys is _MISSING
            else unknown_keys
        )
        use_error_mode = self.error_mode if error_mode is _MISSING else error_mode
        return validate(
            schema,
            data,
            coerce=typing_cast(bool, use_coerce),
            max_depth=typing_cast(int, use_max_depth),
            unknown_keys=typing_cast(UnknownKeysMode, use_unknown_keys),
            error_mode=typing_cast(ErrorMode, use_error_mode),
        )


from . import envfile as _envfile
from .json_schema import to_json_schema
from .schema import Schema, normalize_schema_input, wrap_schema_result
