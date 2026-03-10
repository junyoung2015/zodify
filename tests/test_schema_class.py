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


def test_schema_and_dict_paths_produce_equivalent_success_payloads() -> None:
    class Credentials(Schema):
        username: str
        password: str

    class DatabaseConfig(Schema):
        host: str
        port: int = 5432
        creds: Credentials
        replicas: list[Credentials]

    dict_schema = {
        "host": str,
        "port": zodify.Optional(int, 5432),
        "creds": {"username": str, "password": str},
        "replicas": [{"username": str, "password": str}],
    }
    payload = {
        "host": "db.local",
        "creds": {"username": "kai", "password": "pw"},
        "replicas": [{"username": "kai", "password": "pw"}],
        "extra": "drop-me",
    }

    class_result = validate(DatabaseConfig, payload, unknown_keys="strip")
    dict_result = validate(dict_schema, payload, unknown_keys="strip")

    validator = Validator(unknown_keys="strip")
    class_via_validator = validator.validate(DatabaseConfig, payload)
    dict_via_validator = validator.validate(dict_schema, payload)

    assert dict(class_result) == dict_result
    assert dict(class_via_validator) == dict_via_validator
    assert dict(class_result) == dict(class_via_validator)
    assert json.dumps(class_result, sort_keys=True) == json.dumps(dict_result, sort_keys=True)
    assert isinstance(class_result, DatabaseConfig)
    assert isinstance(class_via_validator, DatabaseConfig)
    assert type(dict_result) is dict
    assert type(dict_via_validator) is dict


def test_schema_and_dict_paths_produce_equivalent_failure_issues() -> None:
    class Credentials(Schema):
        username: str
        password: str

    class DatabaseConfig(Schema):
        host: str
        port: int
        creds: Credentials

    dict_schema = {
        "host": str,
        "port": int,
        "creds": {"username": str, "password": str},
    }
    payload = {
        "host": "db.local",
        "port": "bad",
        "creds": {"username": 7, "password": "pw"},
        "extra": "drop-me",
    }

    with pytest.raises(ValidationError) as class_exc:
        validate(DatabaseConfig, payload, error_mode="structured")

    with pytest.raises(ValidationError) as dict_exc:
        validate(dict_schema, payload, error_mode="structured")

    assert class_exc.value.issues == dict_exc.value.issues
    assert [issue["path"] for issue in class_exc.value.issues] == [
        "port",
        "creds.username",
        "extra",
    ]


def test_schema_result_attribute_and_key_mutation_stay_in_sync() -> None:
    class DatabaseConfig(Schema):
        host: str
        port: int

    result = validate(DatabaseConfig, {"host": "db.local", "port": 5432})

    result.host = "db.internal"
    assert result["host"] == "db.internal"

    result["host"] = "db.external"
    assert result.host == "db.external"

    result.update({"host": "db.updated"})
    assert result.host == "db.updated"

    del result.host
    assert "host" not in result

    with pytest.raises(AttributeError, match="host"):
        _ = result.host

    with pytest.raises(AttributeError, match="missing"):
        _ = result.missing

    result.setdefault("host", "db.setdefault")
    assert result.host == "db.setdefault"

    popped = result.pop("host")
    assert popped == "db.setdefault"
    with pytest.raises(AttributeError, match="host"):
        _ = result.host


def test_defaulted_schema_fields_prefer_validated_payload_over_class_attributes() -> None:
    class Credentials(Schema):
        username: str

    class DatabaseConfig(Schema):
        port: int = 5432
        creds: Credentials = {"username": "kai"}

    result = validate(DatabaseConfig, {})

    assert result.port == 5432
    assert result["port"] == 5432
    assert isinstance(result.creds, Credentials)
    assert result.creds.username == "kai"

    result.port = 15432
    assert result["port"] == 15432
    assert result.port == 15432

    result["port"] = 9000
    assert result.port == 9000


def test_nested_schema_mutation_rewraps_dict_assignments() -> None:
    class Credentials(Schema):
        username: str
        password: str

    class DatabaseConfig(Schema):
        creds: Credentials
        replicas: list[Credentials]

    result = validate(
        DatabaseConfig,
        {
            "creds": {"username": "kai", "password": "pw"},
            "replicas": [{"username": "kai", "password": "pw"}],
        },
    )

    result.creds = {"username": "lee", "password": "next"}
    assert isinstance(result.creds, Credentials)
    assert result.creds.username == "lee"

    result["creds"] = {"username": "park", "password": "third"}
    assert isinstance(result.creds, Credentials)
    assert result.creds.username == "park"

    result.update({"replicas": [{"username": "choi", "password": "fourth"}]})
    assert isinstance(result.replicas[0], Credentials)
    assert result.replicas[0].username == "choi"

    result.replicas.append({"username": "ahn", "password": "fifth"})
    assert isinstance(result.replicas[1], Credentials)
    assert result.replicas[1].username == "ahn"

    result.replicas[0] = {"username": "moon", "password": "sixth"}
    assert isinstance(result.replicas[0], Credentials)
    assert result.replicas[0].username == "moon"

    result.replicas.extend([{"username": "jin", "password": "seventh"}])
    assert isinstance(result.replicas[2], Credentials)
    assert result.replicas[2].username == "jin"

    result.replicas.insert(1, {"username": "han", "password": "eighth"})
    assert isinstance(result.replicas[1], Credentials)
    assert result.replicas[1].username == "han"

    merged = result | {
        "creds": {"username": "park", "password": "ninth"},
        "replicas": [{"username": "ryu", "password": "tenth"}],
    }
    assert isinstance(merged, DatabaseConfig)
    assert isinstance(merged.creds, Credentials)
    assert merged.creds.username == "park"
    assert isinstance(merged.replicas[0], Credentials)
    assert merged.replicas[0].username == "ryu"

    result |= {
        "creds": {"username": "seo", "password": "eleventh"},
        "replicas": [{"username": "yoon", "password": "twelfth"}],
    }
    assert isinstance(result.creds, Credentials)
    assert result.creds.username == "seo"
    assert isinstance(result.replicas[0], Credentials)
    assert result.replicas[0].username == "yoon"

    with pytest.raises(TypeError, match="unsupported operand type\\(s\\) for \\|"):
        result | [("extra", 1)]

    with pytest.raises(TypeError, match="unsupported operand type\\(s\\) for \\|"):
        [("extra", 1)] | result


def test_leading_underscore_schema_fields_remain_synced_with_dict_storage() -> None:
    class SecretConfig(Schema):
        _secret: str

    result = validate(SecretConfig, {"_secret": "x"})

    assert result._secret == "x"
    assert result["_secret"] == "x"

    result._secret = "y"
    assert result._secret == "y"
    assert result["_secret"] == "y"
    assert "_secret" not in getattr(result, "__dict__", {})

    result["_secret"] = "z"
    assert result._secret == "z"

    del result._secret
    with pytest.raises(AttributeError, match="_secret"):
        _ = result._secret


def test_schema_rejects_unsupported_class_surface_with_canonical_messages() -> None:
    with pytest.raises(TypeError, match="Schema declarations cannot be instantiated directly"):
        Schema()

    class ParentSchema(Schema):
        host: str

    with pytest.raises(TypeError, match="Schema declarations cannot be instantiated directly"):
        ParentSchema()

    with pytest.raises(TypeError, match="ChildSchema: inheritance beyond direct Schema subclassing is unsupported"):
        class ChildSchema(ParentSchema):
            port: int

    namespace: dict[str, object] = {"Schema": Schema}
    with pytest.raises(TypeError, match="Node.child: forward references are unsupported"):
        exec(
            "class Node(Schema):\n"
            "    child: 'Node'\n",
            namespace,
            namespace,
        )

    with pytest.raises(TypeError, match="FutureStyle.host: forward references are unsupported"):
        exec(
            "class FutureStyle(Schema):\n"
            "    host: 'str'\n",
            namespace,
            namespace,
        )

    with pytest.raises(
        TypeError,
        match="BadDictSchema.metadata: parameterized dict annotations are unsupported; use bare dict or nested Schema",
    ):
        class BadDictSchema(Schema):
            metadata: dict[str, int]

    with pytest.raises(TypeError, match="DeferredCustomValidator.port: callable field validators are deferred"):
        class DeferredCustomValidator(Schema):
            port: staticmethod = staticmethod(lambda value: value > 0)

    with pytest.raises(
        TypeError,
        match="CollisionSchema.items: dict method names are unsupported in Schema fields; use plain dict schemas for those cases",
    ):
        class CollisionSchema(Schema):
            items: str

    with pytest.raises(
        TypeError,
        match="BadNameSchema.bad-field: invalid identifier field names are unsupported; use plain dict schemas for those cases",
    ):
        type("BadNameSchema", (Schema,), {"__annotations__": {"bad-field": str}})

    with pytest.raises(
        TypeError,
        match="KeywordSchema.class: invalid identifier field names are unsupported; use plain dict schemas for those cases",
    ):
        type("KeywordSchema", (Schema,), {"__annotations__": {"class": str}})

    with pytest.raises(
        TypeError,
        match="NeedsConcrete.child: nested fields must use a concrete Schema subclass",
    ):
        class NeedsConcrete(Schema):
            child: Schema

    with pytest.raises(
        TypeError,
        match="MaybeCredentials.creds: unions containing Schema subclasses or parameterized containers are unsupported; use plain dict schemas for those cases",
    ):
        class MaybeCredentials(Schema):
            creds: ParentSchema | None

    with pytest.raises(
        TypeError,
        match="MaybeList.entries: unions containing Schema subclasses or parameterized containers are unsupported; use plain dict schemas for those cases",
    ):
        class MaybeList(Schema):
            entries: list[int] | None


def test_schema_ignores_unannotated_control_objects() -> None:
    class ConfiguredSchema(Schema):
        model_config = {"frozen": True}
        registry = {"primary": "db"}
        cache = {"ttl": 60}
        host: str

    assert ConfiguredSchema.__zodify_schema__ == {"host": str}
    assert ConfiguredSchema.model_config == {"frozen": True}
    assert ConfiguredSchema.registry == {"primary": "db"}
    assert ConfiguredSchema.cache == {"ttl": 60}

    result = validate(ConfiguredSchema, {"host": "db.local"})

    assert result.host == "db.local"


def test_schema_path_preserves_unknown_key_errors_structured_errors_depth_and_coercion() -> None:
    class Credentials(Schema):
        username: str

    class DatabaseConfig(Schema):
        host: str
        port: int
        creds: Credentials

    with pytest.raises(ValueError, match="extra: unknown key"):
        validate(
            DatabaseConfig,
            {"host": "db.local", "port": 5432, "creds": {"username": "kai"}, "extra": "drop-me"},
        )

    with pytest.raises(ValidationError) as exc_info:
        Validator().validate(
            DatabaseConfig,
            {"host": "db.local", "port": 5432, "creds": {"username": "kai"}, "extra": "drop-me"},
            error_mode="structured",
        )

    assert exc_info.value.issues == [
        {
            "path": "extra",
            "message": "unknown key",
            "expected": "known",
            "got": "unknown",
        }
    ]

    with pytest.raises(ValueError, match="port: cannot coerce 'oops' to int"):
        validate(
            DatabaseConfig,
            {"host": "db.local", "port": "oops", "creds": {"username": "kai"}},
            coerce=True,
        )

    with pytest.raises(ValueError, match="creds: max depth exceeded"):
        validate(
            DatabaseConfig,
            {"host": "db.local", "port": 5432, "creds": {"username": "kai"}},
            max_depth=1,
        )


def test_schema_supports_typing_optional_annotations() -> None:
    class LegacyOptionalSchema(Schema):
        timeout: Optional[int]

    assert LegacyOptionalSchema.__zodify_schema__["timeout"] == (int | None)
    assert validate(LegacyOptionalSchema, {"timeout": None}).timeout is None


def test_schema_supports_bare_list_annotations() -> None:
    class RawListSchema(Schema):
        entries: list

    assert RawListSchema.__zodify_schema__["entries"] is list

    result = validate(RawListSchema, {"entries": [1, "two", 3.0]})

    assert result.entries == [1, "two", 3.0]
    assert result["entries"] == [1, "two", 3.0]


def sink(**kwargs: object) -> None:
    assert kwargs["host"] == "db.local"
