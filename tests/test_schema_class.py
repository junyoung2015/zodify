"""Live runtime coverage for the public Schema API."""

import json
from typing import ClassVar, Optional, Union

import pytest
import zodify
from zodify import Schema, ValidationError, Validator, validate


def test_schema_public_surface_uses_the_approved_extracted_module_boundary() -> None:
    assert "Schema" in zodify.__all__
    assert zodify.Schema is Schema
    assert not hasattr(zodify, "ValidatedDict")


def test_schema_subclass_compiles_plain_dict_schema_at_definition_time() -> None:
    class Credentials(Schema):
        username: str
        password: str

    class DatabaseConfig(Schema):
        host: str
        port: int = 5432
        creds: Credentials
        replicas: list[Credentials]
        timeout: Optional[int]
        metadata: dict
        tags: list[int]
        mode: Union[str, int]
        __secret__: str
        helper_constant: ClassVar[str] = "ignore-me"

        def helper(self) -> str:
            return "ignore-me"

    compiled = DatabaseConfig.__zodify_schema__
    assert compiled["host"] is str
    assert isinstance(compiled["port"], zodify.Optional)
    assert compiled["port"].type is int
    assert compiled["port"].default == 5432
    assert compiled["creds"] == Credentials.__zodify_schema__
    assert compiled["replicas"] == [Credentials.__zodify_schema__]
    assert compiled["timeout"] == (int | None)
    assert compiled["metadata"] is dict
    assert compiled["tags"] == [int]
    assert compiled["mode"] == (str | int)
    assert "__secret__" not in compiled
    assert "helper_constant" not in compiled
    assert "helper" not in compiled
    assert type(Schema) is type


def test_validate_schema_returns_wrapped_result_and_normalizes_engine_input(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}
    original_validate = zodify._validate

    def recording_validate(schema, data, coerce, prefix, errors, depth, unknown_keys):
        if prefix == "":
            captured["schema_type"] = type(schema)
            captured["schema"] = schema
        return original_validate(schema, data, coerce, prefix, errors, depth, unknown_keys)

    class Credentials(Schema):
        username: str
        password: str

    class DatabaseConfig(Schema):
        host: str
        port: int = 5432
        creds: Credentials
        replicas: list[Credentials]

    monkeypatch.setattr(zodify, "_validate", recording_validate)
    result = validate(
        DatabaseConfig,
        {
            "host": "db.local",
            "creds": {"username": "kai", "password": "pw"},
            "replicas": [{"username": "kai", "password": "pw"}],
        },
    )

    assert isinstance(result, dict)
    assert isinstance(result, DatabaseConfig)
    assert result.host == "db.local"
    assert result.port == 5432
    assert result["port"] == 5432
    assert result.creds.username == "kai"
    assert isinstance(result.creds, Credentials)
    assert result.replicas[0].username == "kai"
    assert isinstance(result.replicas[0], Credentials)
    assert json.dumps(result) == (
        '{"host": "db.local", "port": 5432, "creds": '
        '{"username": "kai", "password": "pw"}, "replicas": '
        '[{"username": "kai", "password": "pw"}]}'
    )
    assert dict(result)["host"] == "db.local"
    assert captured["schema_type"] is dict
    assert captured["schema"] == DatabaseConfig.__zodify_schema__

    sink(**result)


def test_schema_supports_typing_union_annotations() -> None:
    class LegacyUnionSchema(Schema):
        mode: Union[str, int]

    assert LegacyUnionSchema.__zodify_schema__["mode"] == (str | int)
    assert validate(LegacyUnionSchema, {"mode": "safe"}).mode == "safe"
    assert validate(LegacyUnionSchema, {"mode": 7}).mode == 7


def test_validator_validate_delegates_to_public_validate_and_preserves_wrapper(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}
    original_validate = zodify.validate

    def recording_validate(schema, data, **kwargs):
        captured["schema"] = schema
        captured["kwargs"] = kwargs
        return original_validate(schema, data, **kwargs)

    class DatabaseConfig(Schema):
        host: str

    payload = {"host": "db.local", "extra": "drop-me"}

    monkeypatch.setattr(zodify, "validate", recording_validate)
    result = Validator().validate(DatabaseConfig, payload, unknown_keys="strip")

    assert captured["schema"] is DatabaseConfig
    assert captured["kwargs"] == {"coerce": False, "max_depth": 32, "unknown_keys": "strip", "error_mode": "text"}
    assert isinstance(result, DatabaseConfig)
    assert result.host == "db.local"
    assert "extra" not in result


def test_plain_dict_schema_still_returns_plain_dict() -> None:
    result = validate({"host": str, "port": int}, {"host": "db.local", "port": 5432})

    assert type(result) is dict
    assert not isinstance(result, Schema)


def sink(**kwargs: object) -> None:
    assert kwargs["host"] == "db.local"
