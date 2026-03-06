"""Runtime coverage for schema-class prototype behavior."""

import json
from typing import ClassVar

import pytest
import zodify

from tests.typing import schema_class_runtime_prototype as prototype


def test_prototype_module_is_importable() -> None:
    assert prototype.Schema is not None


def test_schema_subclass_generates_plain_dict_schema_at_definition_time() -> None:
    class Credentials(prototype.Schema):
        username: str
        password: str

    class DatabaseConfig(prototype.Schema):
        host: str
        port: int = 5432
        creds: Credentials
        metadata: dict
        tags: list[int]
        mode: str | int
        helper_constant: ClassVar[str] = "ignore-me"

        def helper(self) -> str:
            return "ignore-me"

    compiled = DatabaseConfig.__zodify_schema__
    assert compiled["host"] is str
    assert isinstance(compiled["port"], zodify.Optional)
    assert compiled["port"].type is int
    assert compiled["port"].default == 5432
    assert compiled["creds"] == Credentials.__zodify_schema__
    assert compiled["metadata"] is dict
    assert compiled["tags"] == [int]
    assert compiled["mode"] == (str | int)
    assert type(prototype.Schema) is type


def test_validate_schema_returns_wrapped_dict_with_attribute_access_and_nested_wrapping() -> None:
    captured: dict[str, object] = {}
    original_validate = zodify.validate

    def recording_validate(schema, data, **kwargs):
        captured["schema_type"] = type(schema)
        captured["schema"] = schema
        return original_validate(schema, data, **kwargs)

    class Credentials(prototype.Schema):
        username: str
        password: str

    class DatabaseConfig(prototype.Schema):
        host: str
        port: int = 5432
        creds: Credentials

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(zodify, "validate", recording_validate)
    try:
        result = prototype.validate(
            DatabaseConfig,
            {"host": "db.local", "creds": {"username": "kai", "password": "pw"}},
        )
    finally:
        monkeypatch.undo()

    assert isinstance(result, dict)
    assert isinstance(result, prototype.ValidatedDict)
    assert isinstance(result, DatabaseConfig)
    assert result.host == "db.local"
    assert result["port"] == 5432
    assert result.creds.username == "kai"
    assert isinstance(result.creds, dict)
    assert json.dumps(result) == (
        '{"host": "db.local", "port": 5432, "creds": '
        '{"username": "kai", "password": "pw"}}'
    )
    assert dict(result)["host"] == "db.local"
    assert captured["schema_type"] is dict
    assert captured["schema"] == DatabaseConfig.__zodify_schema__

    sink(**result)


def test_plain_dict_schema_still_returns_plain_dict() -> None:
    result = prototype.validate({"host": str, "port": int}, {"host": "db.local", "port": 5432})

    assert type(result) is dict
    assert not isinstance(result, prototype.ValidatedDict)


def test_validator_wrapper_accepts_schema_subclass_without_changing_runtime_engine_contract() -> None:
    captured: dict[str, object] = {}
    original_validate = zodify.validate

    def recording_validate(schema, data, **kwargs):
        captured["schema_type"] = type(schema)
        captured["schema"] = schema
        return original_validate(schema, data, **kwargs)

    class DatabaseConfig(prototype.Schema):
        host: str

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(zodify, "validate", recording_validate)
    try:
        result = prototype.Validator().validate(DatabaseConfig, {"host": "db.local"})
    finally:
        monkeypatch.undo()

    assert result.host == "db.local"
    assert captured["schema_type"] is dict
    assert captured["schema"] == {"host": str}


def test_missing_attributes_raise_attribute_error_and_field_mutation_stays_in_sync() -> None:
    class DatabaseConfig(prototype.Schema):
        host: str
        port: int

    result = prototype.validate(DatabaseConfig, {"host": "db.local", "port": 5432})

    result.host = "db.internal"
    assert result["host"] == "db.internal"

    del result.host
    assert "host" not in result

    with pytest.raises(AttributeError, match="host"):
        _ = result.host

    with pytest.raises(AttributeError, match="missing"):
        _ = result.missing


def test_field_name_collisions_and_unsupported_forward_refs_are_explicit() -> None:
    class CollisionSchema(prototype.Schema):
        items: str
        valid_name: str

    result = prototype.validate(CollisionSchema, {"items": "value", "valid_name": "ok"})

    assert callable(result.items)
    assert result["items"] == "value"
    assert result.valid_name == "ok"

    with pytest.raises(TypeError, match="forward references are unsupported"):
        namespace: dict[str, object] = {"Schema": prototype.Schema}
        exec(
            "class Node(Schema):\n"
            "    child: 'Node'\n",
            namespace,
            namespace,
        )


def test_custom_validator_bridge_is_explicitly_rejected_in_the_prototype() -> None:
    with pytest.raises(TypeError, match="callable field validators are deferred"):
        class DeferredCustomValidator(prototype.Schema):
            port: staticmethod = staticmethod(lambda value: value > 0)


def sink(**kwargs: object) -> None:
    assert kwargs["host"] == "db.local"
