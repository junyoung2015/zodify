# pyright: strict
"""Typing contract for class and ordinary dict JSON input."""

from typing import TYPE_CHECKING, Any

from zodify import Schema
from zodify.json_io import JSONInputError, validate_json

if TYPE_CHECKING:
    class Config(Schema):
        port: int
        name: str

    config: Config = validate_json(Config, '{"port":8080,"name":"svc"}')
    port: int = config.port
    raw: dict[str, Any] = validate_json({"port": int}, b'{"port":8080}')
    code: str = JSONInputError("invalid_json").code
    line: int | None = JSONInputError("invalid_json").line
