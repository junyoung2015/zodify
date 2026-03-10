"""Runtime coverage for the executable schema reference module."""

import importlib.util
import json
from pathlib import Path
from typing import ClassVar, Optional, Union

import pytest
import zodify

from tests.typing import schema_reference_module as contract

MIRROR_PATH = Path(contract.__file__).resolve()


def _load_contract_module():
    spec = importlib.util.spec_from_file_location(
        "schema_reference_module_runtime",
        MIRROR_PATH,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def test_reference_module_source_is_present() -> None:
    assert MIRROR_PATH.exists()


def test_contract_module_is_importable() -> None:
    module = _load_contract_module()
    assert module.Schema is not None


def test_artifact_schema_subclass_generates_plain_dict_schema_at_definition_time() -> None:
    module = _load_contract_module()

    class Credentials(module.Schema):
        username: str
        password: str

    class DatabaseConfig(module.Schema):
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
    assert type(module.Schema) is type


def test_artifact_validate_schema_returns_wrapped_dict_with_attribute_access_and_nested_wrapping(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_contract_module()
    captured: dict[str, object] = {}
    original_validate = zodify.validate

    def recording_validate(schema, data, **kwargs):
        captured["schema_type"] = type(schema)
        captured["schema"] = schema
        return original_validate(schema, data, **kwargs)

    class Credentials(module.Schema):
        username: str
        password: str

    class DatabaseConfig(module.Schema):
        host: str
        port: int = 5432
        creds: Credentials
        replicas: list[Credentials]

    monkeypatch.setattr(zodify, "validate", recording_validate)
    result = module.validate(
        DatabaseConfig,
        {
            "host": "db.local",
            "creds": {"username": "kai", "password": "pw"},
            "replicas": [{"username": "kai", "password": "pw"}],
        },
    )

    assert isinstance(result, dict)
    assert isinstance(result, module.ValidatedDict)
    assert isinstance(result, DatabaseConfig)
    assert result.host == "db.local"
    assert result.port == 5432
    assert result["port"] == 5432
    assert result.creds.username == "kai"
    assert isinstance(result.creds, dict)
    assert result.replicas[0].username == "kai"
    assert isinstance(result.replicas[0], dict)
    assert json.dumps(result) == (
        '{"host": "db.local", "port": 5432, "creds": '
        '{"username": "kai", "password": "pw"}, "replicas": '
        '[{"username": "kai", "password": "pw"}]}'
    )
    assert dict(result)["host"] == "db.local"
    assert captured["schema_type"] is dict
    assert captured["schema"] == DatabaseConfig.__zodify_schema__

    sink(**result)


def test_artifact_schema_supports_typing_union_annotations() -> None:
    module = _load_contract_module()

    class LegacyUnionSchema(module.Schema):
        mode: Union[str, int]

    assert LegacyUnionSchema.__zodify_schema__["mode"] == (str | int)
    assert module.validate(LegacyUnionSchema, {"mode": "safe"}).mode == "safe"
    assert module.validate(LegacyUnionSchema, {"mode": 7}).mode == 7


def test_artifact_plain_dict_schema_still_returns_plain_dict() -> None:
    module = _load_contract_module()
    result = module.validate({"host": str, "port": int}, {"host": "db.local", "port": 5432})

    assert type(result) is dict
    assert not isinstance(result, module.ValidatedDict)


def test_artifact_validator_accepts_schema_subclass_without_changing_runtime_engine_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_contract_module()
    captured: dict[str, object] = {}
    original_validate = zodify.validate

    def recording_validate(schema, data, **kwargs):
        captured["schema_type"] = type(schema)
        captured["schema"] = schema
        return original_validate(schema, data, **kwargs)

    class DatabaseConfig(module.Schema):
        host: str

    monkeypatch.setattr(zodify, "validate", recording_validate)
    result = module.Validator().validate(DatabaseConfig, {"host": "db.local"})

    assert result.host == "db.local"
    assert captured["schema_type"] is dict
    assert captured["schema"] == {"host": str}


def test_artifact_missing_attributes_raise_attribute_error_and_field_mutation_stays_in_sync() -> None:
    module = _load_contract_module()

    class DatabaseConfig(module.Schema):
        host: str
        port: int

    result = module.validate(DatabaseConfig, {"host": "db.local", "port": 5432})

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


def test_artifact_defaulted_schema_fields_prefer_validated_payload_over_class_attributes() -> None:
    module = _load_contract_module()

    class Credentials(module.Schema):
        username: str

    class DatabaseConfig(module.Schema):
        port: int = 5432
        creds: Credentials = {"username": "kai"}

    result = module.validate(DatabaseConfig, {})

    assert result.port == 5432
    assert result["port"] == 5432
    assert isinstance(result.creds, Credentials)
    assert result.creds.username == "kai"

    result.port = 15432
    assert result["port"] == 15432
    assert result.port == 15432

    result["port"] = 9000
    assert result.port == 9000


def test_artifact_nested_schema_mutation_rewraps_dict_assignments() -> None:
    module = _load_contract_module()

    class Credentials(module.Schema):
        username: str
        password: str

    class DatabaseConfig(module.Schema):
        creds: Credentials
        replicas: list[Credentials]

    result = module.validate(
        DatabaseConfig,
        {
            "creds": {"username": "kai", "password": "pw"},
            "replicas": [{"username": "kai", "password": "pw"}],
        },
    )

    result.creds = {"username": "lee", "password": "next"}
    assert result.creds.username == "lee"

    result["creds"] = {"username": "park", "password": "third"}
    assert result.creds.username == "park"

    result.update({"replicas": [{"username": "choi", "password": "fourth"}]})
    assert result.replicas[0].username == "choi"

    merged = result | {
        "creds": {"username": "park", "password": "fifth"},
        "replicas": [{"username": "ryu", "password": "sixth"}],
    }
    assert isinstance(merged, DatabaseConfig)
    assert merged.creds.username == "park"
    assert merged.replicas[0].username == "ryu"

    result |= {
        "creds": {"username": "seo", "password": "seventh"},
        "replicas": [{"username": "yoon", "password": "eighth"}],
    }
    assert result.creds.username == "seo"
    assert result.replicas[0].username == "yoon"

    with pytest.raises(TypeError, match="unsupported operand type\\(s\\) for \\|"):
        result | [("extra", 1)]

    with pytest.raises(TypeError, match="unsupported operand type\\(s\\) for \\|"):
        [("extra", 1)] | result


def test_artifact_leading_underscore_schema_fields_remain_synced_with_dict_storage() -> None:
    module = _load_contract_module()

    class SecretConfig(module.Schema):
        _secret: str

    result = module.validate(SecretConfig, {"_secret": "x"})

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


def test_artifact_unsupported_surface_and_forward_refs_are_explicit() -> None:
    module = _load_contract_module()

    with pytest.raises(TypeError, match="Schema declarations cannot be instantiated directly"):
        module.Schema()

    class ParentSchema(module.Schema):
        host: str

    with pytest.raises(TypeError, match="Schema declarations cannot be instantiated directly"):
        ParentSchema()

    with pytest.raises(
        TypeError,
        match="CollisionSchema.items: dict method names are unsupported in Schema fields; use plain dict schemas for those cases",
    ):
        class CollisionSchema(module.Schema):
            items: str

    with pytest.raises(TypeError, match="forward references are unsupported"):
        namespace: dict[str, object] = {"Schema": module.Schema}
        exec(
            "class Node(Schema):\n"
            "    child: 'Node'\n",
            namespace,
            namespace,
        )

    with pytest.raises(
        TypeError,
        match="MaybeCredentials.creds: unions containing Schema subclasses or parameterized containers are unsupported; use plain dict schemas for those cases",
    ):
        class MaybeCredentials(module.Schema):
            creds: ParentSchema | None

    with pytest.raises(
        TypeError,
        match="MaybeList.entries: unions containing Schema subclasses or parameterized containers are unsupported; use plain dict schemas for those cases",
    ):
        class MaybeList(module.Schema):
            entries: list[int] | None


def test_artifact_postponed_string_annotations_are_explicitly_unsupported() -> None:
    module = _load_contract_module()
    namespace: dict[str, object] = {"Schema": module.Schema}

    with pytest.raises(TypeError, match="forward references are unsupported"):
        exec(
            "class FutureStyle(Schema):\n"
            "    host: 'str'\n",
            namespace,
            namespace,
        )


def test_artifact_custom_validator_bridge_is_explicitly_rejected() -> None:
    module = _load_contract_module()

    with pytest.raises(TypeError, match="callable field validators are deferred"):
        class DeferredCustomValidator(module.Schema):
            port: staticmethod = staticmethod(lambda value: value > 0)


def test_artifact_strip_mode_preserves_schema_wrapper_for_both_entrypoints() -> None:
    module = _load_contract_module()

    class DatabaseConfig(module.Schema):
        host: str

    payload = {"host": "db.local", "extra": "drop-me"}

    direct = module.validate(DatabaseConfig, payload, unknown_keys="strip")
    via_validator = module.Validator().validate(DatabaseConfig, payload, unknown_keys="strip")

    assert isinstance(direct, DatabaseConfig)
    assert isinstance(via_validator, DatabaseConfig)
    assert direct.host == "db.local"
    assert via_validator.host == "db.local"
    assert "extra" not in direct
    assert "extra" not in via_validator


def test_artifact_unknown_keys_reject_and_structured_errors_match_dict_engine() -> None:
    module = _load_contract_module()

    class DatabaseConfig(module.Schema):
        host: str

    with pytest.raises(ValueError, match="extra: unknown key"):
        module.validate(DatabaseConfig, {"host": "db.local", "extra": "drop-me"})

    with pytest.raises(zodify.ValidationError) as exc_info:
        module.Validator().validate(
            DatabaseConfig,
            {"host": "db.local", "extra": "drop-me"},
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


def test_artifact_schema_path_preserves_depth_and_coercion_failures() -> None:
    module = _load_contract_module()

    class Credentials(module.Schema):
        username: str

    class DatabaseConfig(module.Schema):
        port: int
        creds: Credentials

    with pytest.raises(ValueError, match="port: cannot coerce 'oops' to int"):
        module.validate(DatabaseConfig, {"port": "oops", "creds": {"username": "kai"}}, coerce=True)

    with pytest.raises(ValueError, match="max depth exceeded"):
        module.Validator().validate(
            DatabaseConfig,
            {"port": 5432, "creds": {"username": "kai"}},
            max_depth=1,
        )


def test_artifact_inheritance_beyond_direct_schema_subclassing_is_explicitly_rejected() -> None:
    module = _load_contract_module()

    class BaseConfig(module.Schema):
        host: str

    with pytest.raises(
        TypeError,
        match="inheritance beyond direct Schema subclassing is unsupported",
    ):
        class ChildConfig(BaseConfig):
            port: int


def test_artifact_parameterized_dict_annotations_are_explicitly_rejected() -> None:
    module = _load_contract_module()

    with pytest.raises(
        TypeError,
        match="parameterized dict annotations are unsupported",
        ):
        class TypedDictField(module.Schema):
            settings: dict[str, int]


def test_artifact_invalid_identifier_field_names_are_explicitly_rejected() -> None:
    module = _load_contract_module()

    namespace: dict[str, object] = {"Schema": module.Schema, "str": str}
    with pytest.raises(
        TypeError,
        match="invalid identifier field names are unsupported",
    ):
        exec(
            "class InvalidIdentifierField(Schema):\n"
            "    __annotations__ = {'bad-name': str}\n",
            namespace,
            namespace,
        )

    with pytest.raises(
        TypeError,
        match="invalid identifier field names are unsupported",
    ):
        exec(
            "class KeywordField(Schema):\n"
            "    __annotations__ = {'class': str}\n",
            namespace,
            namespace,
        )


def test_artifact_base_schema_annotations_require_concrete_subclasses() -> None:
    module = _load_contract_module()

    with pytest.raises(
        TypeError,
        match="nested fields must use a concrete Schema subclass",
    ):
        class InvalidNestedSchema(module.Schema):
            child: module.Schema


def test_artifact_schema_supports_typing_optional_annotations() -> None:
    module = _load_contract_module()

    class LegacyOptionalSchema(module.Schema):
        timeout: Optional[int]

    assert LegacyOptionalSchema.__zodify_schema__["timeout"] == (int | None)
    assert module.validate(LegacyOptionalSchema, {"timeout": None}).timeout is None


def sink(**kwargs: object) -> None:
    assert kwargs["host"] == "db.local"
