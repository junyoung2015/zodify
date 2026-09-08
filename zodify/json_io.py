"""Strict JSON object parsing followed by ordinary Zodify validation."""

from __future__ import annotations

import json
import math
from typing import Any, TypeVar, overload

from . import ErrorMode, UnknownKeysMode, validate
from .schema import Schema

_SchemaT = TypeVar("_SchemaT", bound=Schema)


class JSONInputError(ValueError):
    """Generic source/root error with no source snippet or decoder exception.

    Attributes code, line, and column are safe diagnostic metadata. Python
    tracebacks can still reference caller locals; this is not logging isolation.
    """

    def __init__(self, code: str, *, line: int | None = None, column: int | None = None) -> None:
        self.code = code
        self.line = line
        self.column = column
        super().__init__(f"JSON input rejected: {code}")

    def __reduce__(self) -> tuple[Any, ...]:
        return (self.__class__, (self.code,), self.__dict__)


def _object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise JSONInputError("duplicate_key")
        result[key] = value
    return result


def _constant(token: str) -> Any:
    raise JSONInputError("non_finite_number")


def _float(token: str) -> float:
    value = float(token)
    if not math.isfinite(value):
        raise JSONInputError("non_finite_number")
    return value


def _parse(source: str | bytes, max_bytes: int | None) -> dict[str, Any]:
    failure: JSONInputError | None = None
    try:
        size = len(source) if isinstance(source, bytes) else len(source.encode("utf-8"))
        if max_bytes is not None and size > max_bytes:
            raise JSONInputError("input_too_large")
        text = source.decode("utf-8") if isinstance(source, bytes) else source
        if text.startswith("\ufeff"):
            raise JSONInputError("bom_not_allowed")
        result = json.loads(text, object_pairs_hook=_object, parse_constant=_constant, parse_float=_float)
        if type(result) is not dict:
            raise JSONInputError("object_root_required")
        return result
    except UnicodeError:
        failure = JSONInputError("invalid_utf8")
    except json.JSONDecodeError as exc:
        failure = JSONInputError("invalid_json", line=exc.lineno, column=exc.colno)
    except JSONInputError as exc:
        failure = JSONInputError(exc.code)
    except (ValueError, RecursionError):
        failure = JSONInputError("invalid_json")
    # Raise outside the handler so JSONDecodeError.doc is not retained as context.
    raise failure


@overload
def validate_json(
    schema: type[_SchemaT], source: str | bytes, *, max_bytes: int | None = None,
    coerce: bool = False, max_depth: int = 32, unknown_keys: UnknownKeysMode = "reject",
    error_mode: ErrorMode = "text",
) -> _SchemaT:
    ...


@overload
def validate_json(
    schema: dict[str, Any], source: str | bytes, *, max_bytes: int | None = None,
    coerce: bool = False, max_depth: int = 32, unknown_keys: UnknownKeysMode = "reject",
    error_mode: ErrorMode = "text",
) -> dict[str, Any]:
    ...


def validate_json(
    schema: type[_SchemaT] | dict[str, Any], source: str | bytes, *, max_bytes: int | None = None,
    coerce: bool = False, max_depth: int = 32, unknown_keys: UnknownKeysMode = "reject",
    error_mode: ErrorMode = "text",
) -> _SchemaT | dict[str, Any]:
    """Parse str/UTF-8 bytes and validate one object with ordinary semantics.

    Duplicate keys, BOMs, nonfinite numbers (including overflow), invalid UTF-8,
    and non-object roots raise JSONInputError. max_bytes is a nonnegative UTF-8
    byte limit checked before decoding; counting text bytes allocates an encoded
    copy. It cannot undo the caller's allocation. max_depth applies after parsing
    and counts dict traversals, not parser allocation or total container depth.
    Schema, option, and application-data failures retain ordinary exception types.
    """
    if type(source) not in (str, bytes):
        raise TypeError("source must be str or UTF-8 bytes")
    if max_bytes is not None and (type(max_bytes) is not int or max_bytes < 0):
        raise ValueError("max_bytes must be a nonnegative integer or None")
    data = _parse(source, max_bytes)
    return validate(schema, data, coerce=coerce, max_depth=max_depth, unknown_keys=unknown_keys, error_mode=error_mode)
