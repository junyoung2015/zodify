# pyright: strict, reportUnnecessaryTypeIgnoreComment=error
"""Typing smoke for the live load_env() public API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from zodify import Schema, Validator, load_env


if TYPE_CHECKING:
    class AppConfig(Schema):
        port: int
        debug: bool


    raw = load_env(".env")
    raw_value: str = raw["PORT"]

    structured_raw = load_env(".env", error_mode="structured")
    structured_raw_value: str = structured_raw["PORT"]

    dict_default: dict[str, int] = load_env(
        ".env",
        schema={"PORT": int},
    )
    dict_default_value: int = dict_default["PORT"]

    dict_reject: dict[str, int] = load_env(
        ".env",
        schema={"PORT": int},
        unknown_keys="reject",
    )
    dict_reject_value: int = dict_reject["PORT"]

    dict_strip: dict[str, Any] = load_env(
        ".env",
        schema={"PORT": int},
        unknown_keys="strip",
    )
    dict_strip_value: Any = dict_strip["PORT"]

    schema_validated: AppConfig = load_env(".env", schema=AppConfig)
    schema_port: int = schema_validated.port
    schema_debug: bool = schema_validated.debug

    validator = Validator()
    validator_result: dict[str, int] = validator.validate(
        {"PORT": int},
        load_env(".env"),
        coerce=True,
        max_depth=32,
        unknown_keys="strip",
    )
    validator_value: int = validator_result["PORT"]

    invalid_positional_error_mode = load_env(".env", "structured")  # type: ignore[call-overload]
    invalid_coerce = load_env(".env", coerce=True)  # type: ignore[call-overload]
    invalid_depth = load_env(".env", max_depth=2)  # type: ignore[call-overload]
    invalid_unknown_keys = load_env(".env", unknown_keys="strip")  # type: ignore[call-overload]
