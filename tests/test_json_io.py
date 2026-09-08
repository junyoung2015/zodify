"""Strict parse policies and unchanged ordinary validation semantics."""

import copy
import pickle
from typing import Any

import json

import pytest

from zodify import Optional, Schema, ValidationError, validate
from zodify.json_io import JSONInputError, validate_json


@pytest.mark.parametrize("source", ['{"port":8080,"enabled":true}', b'{"port":8080,"enabled":true}'])
def test_str_and_utf8_bytes(source: str | bytes) -> None:
    assert validate_json({"port": int, "enabled": bool}, source) == {"port": 8080, "enabled": True}


@pytest.mark.parametrize(("source", "code"), [
    ('{"x":1,"x":2}', "duplicate_key"),
    ('{"outer":{"x":1,"x":2}}', "duplicate_key"),
    ('{"x":1,"\\u0078":2}', "duplicate_key"),
    ('{"values":[{"x":1,"x":2}]}', "duplicate_key"),
    ('{"x":NaN}', "non_finite_number"),
    ('{"x":Infinity}', "non_finite_number"),
    ('{"x":-Infinity}', "non_finite_number"),
    ('{"x":1e400}', "non_finite_number"),
    ('{"x":-1e400}', "non_finite_number"),
    ('[]', "object_root_required"),
    ('"secret"', "object_root_required"),
    ('null', "object_root_required"),
    ('1', "object_root_required"),
    ('true', "object_root_required"),
    ('\ufeff{}', "bom_not_allowed"),
    (b'\xef\xbb\xbf{}', "bom_not_allowed"),
    (b'\xff', "invalid_utf8"),
    ('{} trailing', "invalid_json"),
    ('', "invalid_json"),
])
def test_parse_and_root_policies(source: str | bytes, code: str) -> None:
    with pytest.raises(JSONInputError) as exc:
        validate_json({}, source)
    assert exc.value.code == code
    assert exc.value.__context__ is None
    assert exc.value.__cause__ is None


def test_parse_diagnostics_have_position_but_no_source_or_decoder_chain() -> None:
    source = '{\n"password": "SENTINEL_SECRET",\n}'
    with pytest.raises(JSONInputError) as exc:
        validate_json({}, source)
    error = exc.value
    # CPython 3.13 points at the trailing comma; older decoders point at
    # the closing brace. Preserve the active decoder's position, not its text.
    with pytest.raises(json.JSONDecodeError) as decoder:
        json.loads(source)
    assert (error.line, error.column) == (decoder.value.lineno, decoder.value.colno)
    assert "SENTINEL_SECRET" not in str(error)
    assert "SENTINEL_SECRET" not in repr(error.__dict__)
    assert not hasattr(error, "doc")
    assert error.__context__ is None


def test_duplicate_key_diagnostics_do_not_echo_secret_key() -> None:
    with pytest.raises(JSONInputError) as exc:
        validate_json({}, '{"SECRET":1,"SECRET":2}')
    assert "SECRET" not in str(exc.value)
    assert "SECRET" not in repr(exc.value.__dict__)


def test_byte_limits_count_utf8_and_apply_before_decoding() -> None:
    source = '{"name":"한"}'
    byte_length = len(source.encode("utf-8"))
    for payload in [source, source.encode("utf-8")]:
        assert validate_json({"name": str}, payload, max_bytes=byte_length) == {"name": "한"}
        with pytest.raises(JSONInputError) as exc:
            validate_json({"name": str}, payload, max_bytes=byte_length - 1)
        assert exc.value.code == "input_too_large"
    with pytest.raises(JSONInputError) as exc:
        validate_json({}, b'\xff', max_bytes=0)
    assert exc.value.code == "input_too_large"


@pytest.mark.parametrize("limit", [-1, True, 1.5, "10"])
def test_invalid_limit_is_configuration_error(limit: Any) -> None:
    with pytest.raises(ValueError, match="max_bytes") as exc:
        validate_json({}, '{}', max_bytes=limit)
    assert not isinstance(exc.value, JSONInputError)


@pytest.mark.parametrize("source", [None, {}, bytearray(b'{}'), memoryview(b'{}')])
def test_other_sources_refused(source: Any) -> None:
    with pytest.raises(TypeError, match="source"):
        validate_json({}, source)


def test_source_errors_skip_validation_callbacks() -> None:
    calls: list[object] = []

    def predicate(value: object) -> bool:
        calls.append(value)
        return True

    with pytest.raises(JSONInputError):
        validate_json({"x": predicate}, '{"x":1,"x":2}')
    assert calls == []
    assert validate_json({"x": predicate}, '{"x":1}') == {"x": 1}
    assert calls == [1]


def test_options_defaults_and_class_wrapping_delegate_to_ordinary_engine() -> None:
    class Config(Schema):
        port: int
        name: str

    result = validate_json(Config, '{"port":"8080","name":"x","extra":true}', coerce=True, unknown_keys="strip")
    assert isinstance(result, Config)
    assert result.port == 8080
    assert result.name == "x"
    default: list[str] = []
    assert validate_json({"tags": Optional([str], default)}, '{}')["tags"] is default


def test_application_data_errors_preserve_ordinary_issues_and_details() -> None:
    schema = {"port": int}
    with pytest.raises(ValidationError) as adapter:
        validate_json(schema, '{"port":"bad"}', error_mode="structured")
    with pytest.raises(ValidationError) as ordinary:
        validate(schema, {"port": "bad"}, error_mode="structured")
    assert adapter.value.issues == ordinary.value.issues
    assert getattr(adapter.value, "details", None) == getattr(ordinary.value, "details", None)
    assert not isinstance(adapter.value, JSONInputError)


def test_schema_and_option_errors_remain_distinct() -> None:
    with pytest.raises(TypeError):
        validate_json({"x": []}, '{"x":[]}')
    with pytest.raises(ValueError) as exc:
        validate_json({}, '{}', unknown_keys="bad")  # type: ignore[arg-type]
    assert not isinstance(exc.value, JSONInputError)


def test_depth_is_applied_after_parse_with_ordinary_dict_counting() -> None:
    with pytest.raises(ValueError, match="max depth exceeded") as exc:
        validate_json({"child": {}}, '{"child":{}}', max_depth=1)
    assert not isinstance(exc.value, JSONInputError)
    assert validate_json({"items": [[str]]}, '{"items":[["x"]]}', max_depth=1) == {"items": [["x"]]}


def test_finite_floats_and_large_integer_decoder_failure() -> None:
    assert validate_json({"x": float}, '{"x":1e300}') == {"x": 1e300}
    assert validate_json({"x": float}, '{"x":1e-400}') == {"x": 0.0}
    # Huge integer conversion limits are interpreter-specific; either a finite
    # integer or the generic parse category is correct, never a leaked token.
    try:
        result = validate_json({"x": int}, '{"x":' + '9' * 5000 + '}')
    except JSONInputError as exc:
        assert exc.code == "invalid_json"
        assert exc.__context__ is None
    else:
        assert type(result["x"]) is int


def test_error_copy_and_pickle_keep_diagnostic_metadata() -> None:
    error = JSONInputError("invalid_json", line=2, column=3)
    for clone in [copy.copy(error), copy.deepcopy(error), pickle.loads(pickle.dumps(error))]:
        assert (clone.code, clone.line, clone.column) == ("invalid_json", 2, 3)
        assert str(clone) == str(error)
