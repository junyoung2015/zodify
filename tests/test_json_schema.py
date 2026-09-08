"""Exact-export conformance over a bounded JSON instance matrix."""

from itertools import product
from typing import Any

from jsonschema import Draft202012Validator
import pytest

from zodify import Optional, Schema, to_json_schema, validate
from zodify.json_schema import JSONSchemaExport, UnsupportedSchemaError, export_json_schema


def _runtime_accepts(schema: Any, data: dict[str, Any]) -> bool:
    try:
        validate(schema, data)
    except ValueError:
        return False
    return True


def test_result_contract_and_compatibility_facade() -> None:
    result = export_json_schema({"name": str})
    assert isinstance(result, JSONSchemaExport)
    assert (result.fidelity, result.differences, result.schema_draft, result.contract_kind) == (
        "exact", (), "2020-12", "input",
    )
    assert to_json_schema({"name": str}) == result.document
    assert result.document["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert result.document["properties"] == {"name": {"type": "string"}}


def test_exact_keyword_matrix_and_bounded_oracle_conformance() -> None:
    schema = {"required": bool | None, "optional": Optional(str), "items": [{"label": str}]}
    document = to_json_schema(schema)
    Draft202012Validator.check_schema(document)
    assert document["required"] == ["required", "items"]
    assert document["additionalProperties"] is False
    assert document["properties"]["items"]["items"]["additionalProperties"] is False
    oracle = Draft202012Validator(document)
    for flag, optional, items in product(
        [True, False, None, 0, 1.0, "yes", [], {}],
        [{}, {"optional": "ok"}, {"optional": None}, {"unknown": True}],
        [[], [{"label": "x"}], [{"label": True}], [{"label": "x", "extra": None}], [None], {}],
    ):
        data = {"required": flag, "items": items, **optional}
        assert oracle.is_valid(data) is _runtime_accepts(schema, data), data
    for missing in [{}, {"items": []}, {"required": None}]:
        assert oracle.is_valid(missing) is _runtime_accepts(schema, missing)


def test_classes_and_plain_dicts_export_identically() -> None:
    class Credentials(Schema):
        username: str
        enabled: bool | None

    class Service(Schema):
        creds: Credentials
        replicas: list[Credentials]

    document = to_json_schema(Service)
    assert document == to_json_schema(Service.__zodify_schema__)
    Draft202012Validator.check_schema(document)
    for data in [
        {"creds": {"username": "x", "enabled": None}, "replicas": []},
        {"creds": {"username": "x"}, "replicas": []},
        {"creds": {"username": "x", "enabled": True}, "replicas": [{"username": 1, "enabled": None}]},
    ]:
        assert Draft202012Validator(document).is_valid(data) is _runtime_accepts(Service, data)


@pytest.mark.parametrize("declaration", [int, float, int | str, [int], dict, list, set, [], [str, bool]])
def test_numeric_unions_and_unsupported_declarations_rejected(declaration: Any) -> None:
    with pytest.raises(UnsupportedSchemaError) as exc:
        to_json_schema({"a.b": declaration})
    assert exc.value.loc[0] == "a.b"
    assert isinstance(exc.value, TypeError)


def test_integral_float_difference_cannot_silently_escape_exact_mode() -> None:
    assert Draft202012Validator({"type": "integer"}).is_valid(1.0)
    assert not _runtime_accepts({"count": int}, {"count": 1.0})
    for value in [1, 1.0, True]:
        assert _runtime_accepts({"count": int}, {"count": value}) is (type(value) is int)
    with pytest.raises(UnsupportedSchemaError):
        export_json_schema({"count": int})


@pytest.mark.parametrize("default", [None, "ok", 123, [], {}, object()])
def test_all_default_insertion_is_refused(default: Any) -> None:
    with pytest.raises(UnsupportedSchemaError, match="default insertion") as exc:
        to_json_schema({"outer": {"field": Optional(str, default)}})
    assert exc.value.loc == ("outer", "field")


def test_class_defaults_are_also_refused() -> None:
    class Config(Schema):
        name: str = "default"

    with pytest.raises(UnsupportedSchemaError, match="default insertion"):
        to_json_schema(Config)


def test_refusal_does_not_execute_callbacks() -> None:
    calls: list[object] = []

    def callback(value: object) -> bool:
        calls.append(value)
        return True

    with pytest.raises(UnsupportedSchemaError):
        to_json_schema({"token": callback})
    assert calls == []


@pytest.mark.parametrize("key", [1, None, ("x",)])
def test_non_string_keys_reject_at_parent_location(key: Any) -> None:
    with pytest.raises(UnsupportedSchemaError) as exc:
        to_json_schema({"outer": {key: str}})
    assert exc.value.loc == ("outer",)


def test_paths_keep_ambiguous_keys_and_list_indices_distinct() -> None:
    with pytest.raises(UnsupportedSchemaError) as exc:
        to_json_schema({"items[0]": [{"a.b": float}]})
    assert exc.value.loc == ("items[0]", 0, "a.b")


def test_cycles_are_refused_but_shared_dag_is_exportable() -> None:
    cyclic: dict[str, Any] = {}
    cyclic["child"] = cyclic
    with pytest.raises(UnsupportedSchemaError, match="recursive") as exc:
        to_json_schema(cyclic)
    assert exc.value.loc == ("child",)
    shared = {"name": str}
    document = to_json_schema({"a": shared, "b": shared})
    document["properties"]["a"]["properties"]["name"]["type"] = "boolean"
    assert document["properties"]["b"]["properties"]["name"] == {"type": "string"}
    assert shared == {"name": str}


def test_default_dict_depth_boundary() -> None:
    schema: dict[str, Any] = {"name": str}
    data: dict[str, Any] = {"name": "x"}
    for _ in range(31):
        schema, data = {"child": schema}, {"child": data}
    document = to_json_schema(schema)
    assert Draft202012Validator(document).is_valid(data)
    assert validate(schema, data) == data
    with pytest.raises(UnsupportedSchemaError, match="32-dict"):
        to_json_schema({"child": schema})


def test_list_wrapping_preserves_runtime_dict_depth_but_preparation_is_bounded() -> None:
    schema: Any = str
    for _ in range(65):
        schema = [schema]
    with pytest.raises(UnsupportedSchemaError, match="preparation limit"):
        to_json_schema({"items": schema})
    document = to_json_schema({"items": [[{"name": str}]]})
    assert Draft202012Validator(document).is_valid({"items": [[{"name": "x"}]]})


@pytest.mark.parametrize("options", [
    {"coerce": True}, {"unknown_keys": "strip"}, {"max_depth": 31}, {"max_depth": 32.0},
])
def test_non_default_pipeline_is_refused(options: Any) -> None:
    with pytest.raises(UnsupportedSchemaError):
        export_json_schema({"name": str}, **options)


def test_shape_mode_is_not_implicitly_available() -> None:
    with pytest.raises(ValueError, match="fidelity"):
        export_json_schema({"name": str}, fidelity="json-shape")  # type: ignore[arg-type]
