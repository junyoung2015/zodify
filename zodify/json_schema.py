"""Conservative Draft 2020-12 export of the default input acceptance contract."""

from __future__ import annotations

import types
from typing import Any, Literal, NamedTuple, TypeVar

from . import Optional, _MISSING
from .schema import Schema, normalize_schema_input

_SchemaT = TypeVar("_SchemaT", bound=Schema)
_DRAFT_URI = "https://json-schema.org/draft/2020-12/schema"
_PRIMITIVES = {str: "string", bool: "boolean", type(None): "null"}


class UnsupportedSchemaError(TypeError):
    """Export refusal with a structural schema location, never application data."""

    def __init__(self, loc: tuple[str | int, ...], reason: str) -> None:
        self.loc = loc
        self.reason = reason
        super().__init__(f"{loc!r}: {reason}")

    def __reduce__(self) -> tuple[Any, ...]:
        return (self.__class__, (self.loc, self.reason))


class JSONSchemaExport(NamedTuple):
    """An exact input profile; document is a fresh, caller-owned mutable dict."""

    document: dict[str, Any]
    fidelity: Literal["exact"] = "exact"
    differences: tuple[()] = ()
    schema_draft: Literal["2020-12"] = "2020-12"
    contract_kind: Literal["input"] = "input"


def export_json_schema(
    schema: type[_SchemaT] | dict[str, Any], *, fidelity: Literal["exact"] = "exact",
    coerce: bool = False, unknown_keys: Literal["reject", "strip"] = "reject",
    max_depth: int = 32,
) -> JSONSchemaExport:
    """Describe default strict input acceptance over JSON-compatible instances.

    Only fidelity='exact', coerce=False, unknown_keys='reject', and max_depth=32
    are supported. Numeric types, defaults, bare containers, callbacks, cycles,
    and declarations exceeding the depth/preparation profile are refused.
    JSON parser policies and output transformations are outside this contract.
    """
    if fidelity != "exact":
        raise ValueError("fidelity must be 'exact'")
    if coerce is not False or unknown_keys != "reject" or type(max_depth) is not int or max_depth != 32:
        raise UnsupportedSchemaError((), "only coerce=False, unknown_keys='reject', max_depth=32 are exportable")
    normalized, _ = normalize_schema_input(schema)
    document = _export(normalized, (), set(), 0, 0)
    return JSONSchemaExport({"$schema": _DRAFT_URI, **document})


def to_json_schema(schema: type[_SchemaT] | dict[str, Any]) -> dict[str, Any]:
    """Export the exact supported subset as a plain document.

    Args:
        schema: Plain dict or supported Schema class declaration.

    Returns:
        A caller-owned JSON Schema Draft 2020-12 document.

    Raises:
        UnsupportedSchemaError: If the declaration cannot preserve the profile.
        TypeError: If the root is not a supported schema input.

    Example:
        >>> from zodify import to_json_schema
        >>> to_json_schema({"name": str})["properties"]
        {'name': {'type': 'string'}}
    """
    return export_json_schema(schema).document


def _export(schema: Any, loc: tuple[str | int, ...], active: set[int], dict_depth: int, steps: int) -> dict[str, Any]:
    if steps > 64:
        raise UnsupportedSchemaError(loc, "schema exceeds the 64-transition preparation limit")
    if isinstance(schema, (dict, list)):
        if id(schema) in active:
            raise UnsupportedSchemaError(loc, "recursive schema references are unsupported")
        active.add(id(schema))
        try:
            if isinstance(schema, list):
                if len(schema) != 1:
                    raise UnsupportedSchemaError(loc, "list schema must contain exactly one element")
                return {"type": "array", "items": _export(schema[0], loc + (0,), active, dict_depth, steps + 1)}
            if dict_depth >= 32:
                raise UnsupportedSchemaError(loc, "schema exceeds the default 32-dict validation depth")
            properties: dict[str, Any] = {}
            required: list[str] = []
            for key, expected in schema.items():
                if type(key) is not str:
                    raise UnsupportedSchemaError(loc, "object schema keys must be strings")
                child_loc = loc + (key,)
                if isinstance(expected, Optional):
                    if expected.default is not _MISSING:
                        raise UnsupportedSchemaError(child_loc, "default insertion is not exportable")
                    expected = expected.type
                else:
                    required.append(key)
                properties[key] = _export(expected, child_loc, active, dict_depth + 1, steps + 1)
            return {"type": "object", "properties": properties, "required": required, "additionalProperties": False}
        finally:
            active.remove(id(schema))
    if isinstance(schema, types.UnionType):
        return {"anyOf": [_export(member, loc + (i,), active, dict_depth, steps + 1) for i, member in enumerate(schema.__args__)]}
    if type(schema) is type and schema in _PRIMITIVES:
        return {"type": _PRIMITIVES[schema]}
    raise UnsupportedSchemaError(loc, "unsupported declaration: numeric types, bare containers, and callbacks are not exportable")
