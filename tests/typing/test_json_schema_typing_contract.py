# pyright: strict
"""Typing smoke for the exact exporter and compatibility facade."""

from typing import TYPE_CHECKING, Any, Literal

from zodify import Schema, to_json_schema
from zodify.json_schema import JSONSchemaExport, UnsupportedSchemaError, export_json_schema

if TYPE_CHECKING:
    class Credentials(Schema):
        username: str
        enabled: bool | None

    exported_from_dict: dict[str, Any] = to_json_schema({"host": str, "debug": bool})
    exported_from_schema: dict[str, Any] = to_json_schema(Credentials)
    result: JSONSchemaExport = export_json_schema(Credentials)
    document: dict[str, Any] = result.document
    fidelity: Literal["exact"] = result.fidelity
    differences: tuple[()] = result.differences
    schema_path: tuple[str | int, ...] = UnsupportedSchemaError(("items", 0), "unsupported").loc
