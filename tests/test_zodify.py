"""Tests for zodify (zodify)."""

import pytest
from zodify import validate, Optional, __version__


# --- __version__ ---

def test_version():
    assert __version__ == "0.3.0"


# --- PEP 561: py.typed marker ---

def test_py_typed_marker_exists():
    """PEP 561: py.typed marker must exist and be empty."""
    from pathlib import Path
    import zodify
    marker = Path(zodify.__file__).parent / "py.typed"
    assert marker.exists(), "py.typed marker file missing from package"
    assert marker.stat().st_size == 0, "py.typed must be empty per PEP 561"


# --- validate: basic types ---

def test_validate_basic():
    result = validate({"a": int, "b": str}, {"a": 1, "b": "hi"})
    assert result == {"a": 1, "b": "hi"}


def test_validate_type_error_collected():
    with pytest.raises(ValueError) as exc:
        validate({"a": int, "b": str}, {"a": "x", "b": 42})
    msg = str(exc.value)
    assert "a: expected int" in msg
    assert "b: expected str" in msg
    assert "\n" in msg


def test_validate_missing_key():
    with pytest.raises(ValueError, match="missing required key"):
        validate({"a": int}, {})


def test_validate_coercion():
    result = validate(
        {"port": int, "debug": bool},
        {"port": "8080", "debug": "true"},
        coerce=True,
    )
    assert result == {"port": 8080, "debug": True}


def test_validate_extra_keys_stripped():
    assert validate(
        {"a": int}, {"a": 1, "b": 2}, unknown_keys="strip"
    ) == {"a": 1}


def test_validate_bool_int_trap():
    with pytest.raises(ValueError, match="expected int, got bool"):
        validate({"count": int}, {"count": True})


def test_validate_coercion_only_str():
    with pytest.raises(ValueError, match="expected int"):
        validate({"count": int}, {"count": True}, coerce=True)


def test_validate_empty_string_str_valid():
    assert validate({"name": str}, {"name": ""}) == {"name": ""}


def test_validate_empty_string_int_coerce_fails():
    with pytest.raises(ValueError):
        validate({"port": int}, {"port": ""}, coerce=True)


def test_validate_non_dict_data():
    with pytest.raises(TypeError, match="data must be a dict"):
        validate({"a": int}, "not_a_dict")


def test_validate_non_dict_schema():
    with pytest.raises(TypeError, match="schema must be a dict"):
        validate("not_a_schema", {})


def test_validate_bool_coercion_case_insensitive():
    assert validate({"d": bool}, {"d": "TRUE"}, coerce=True) == {"d": True}
    assert validate({"d": bool}, {"d": "Yes"}, coerce=True) == {"d": True}
    assert validate({"d": bool}, {"d": "FALSE"}, coerce=True) == {"d": False}
    assert validate({"d": bool}, {"d": "No"}, coerce=True) == {"d": False}
    assert validate({"d": bool}, {"d": "1"}, coerce=True) == {"d": True}
    assert validate({"d": bool}, {"d": "0"}, coerce=True) == {"d": False}


def test_validate_empty_schema():
    assert validate({}, {"a": 1}, unknown_keys="strip") == {}
    assert validate({}, {}) == {}


def test_validate_none_value():
    with pytest.raises(ValueError, match="expected str"):
        validate({"a": str}, {"a": None})


# --- validate: unsupported schema types ---

def test_validate_set_type_passthrough():
    result = validate({"tags": set}, {"tags": {1, 2, 3}})
    assert result == {"tags": {1, 2, 3}}


def test_validate_tuple_type_passthrough():
    result = validate({"coords": tuple}, {"coords": (1, 2)})
    assert result == {"coords": (1, 2)}


def test_validate_none_type_passthrough():
    result = validate({"x": type(None)}, {"x": None})
    assert result == {"x": None}


def test_validate_set_type_mismatch():
    with pytest.raises(ValueError, match="expected set, got list"):
        validate({"tags": set}, {"tags": [1, 2]})


# --- validate: empty containers ---

def test_validate_empty_list():
    assert validate({"x": list}, {"x": []}) == {"x": []}


def test_validate_empty_dict_value():
    assert validate({"x": dict}, {"x": {}}) == {"x": {}}


# --- validate: numeric edge cases ---

def test_validate_float_inf():
    result = validate({"x": float}, {"x": float("inf")})
    assert result["x"] == float("inf")


def test_validate_float_nan():
    import math
    result = validate({"x": float}, {"x": float("nan")})
    assert math.isnan(result["x"])


def test_validate_very_large_int():
    big = 10**100
    assert validate({"x": int}, {"x": big}) == {"x": big}


def test_validate_negative_zero():
    result = validate({"x": float}, {"x": -0.0})
    assert result == {"x": -0.0}


def test_coerce_inf_string_to_float():
    result = validate({"x": float}, {"x": "inf"}, coerce=True)
    assert result["x"] == float("inf")


def test_coerce_nan_string_to_float():
    import math
    result = validate({"x": float}, {"x": "nan"}, coerce=True)
    assert math.isnan(result["x"])


# --- validate: string coercion edge cases ---

def test_coerce_whitespace_only_to_int_fails():
    with pytest.raises(ValueError):
        validate({"x": int}, {"x": " "}, coerce=True)


def test_coerce_padded_number_to_int():
    result = validate({"x": int}, {"x": " 42 "}, coerce=True)
    assert result == {"x": 42}


def test_validate_unicode_string():
    assert validate({"x": str}, {"x": "héllo"}) == {"x": "héllo"}


def test_coerce_non_str_to_str():
    result = validate({"x": str}, {"x": 42}, coerce=True)
    assert result == {"x": "42"}


# --- validate: bool boundary cases ---

def test_coerce_invalid_bool_string():
    with pytest.raises(ValueError, match="cannot coerce 'maybe' to bool"):
        validate({"x": bool}, {"x": "maybe"}, coerce=True)


def test_coerce_numeric_string_not_bool():
    with pytest.raises(ValueError, match="cannot coerce '2' to bool"):
        validate({"x": bool}, {"x": "2"}, coerce=True)


def test_coerce_mixed_case_bool():
    assert validate({"x": bool}, {"x": "tRuE"}, coerce=True) == {"x": True}
    assert validate({"x": bool}, {"x": "FaLsE"}, coerce=True) == {"x": False}


def test_coerce_whitespace_padded_bool_fails():
    with pytest.raises(ValueError, match="cannot coerce"):
        validate({"x": bool}, {"x": " true "}, coerce=True)


# --- validate: nested dicts ---

def test_nested_dict_happy_path():
    schema = {"db": {"host": str, "port": int}}
    data = {"db": {"host": "localhost", "port": 5432}}
    assert validate(schema, data) == {
        "db": {"host": "localhost", "port": 5432}
    }


def test_nested_dict_type_mismatch():
    with pytest.raises(ValueError, match="db.port: expected int"):
        validate(
            {"db": {"host": str, "port": int}},
            {"db": {"host": "localhost", "port": "bad"}},
        )


def test_nested_dict_value_not_dict():
    with pytest.raises(
        ValueError, match="db: expected dict, got str"
    ):
        validate({"db": {"host": str}}, {"db": "notadict"})


def test_nested_dict_with_coercion():
    result = validate(
        {"db": {"host": str, "port": int}},
        {"db": {"host": "localhost", "port": "5432"}},
        coerce=True,
    )
    assert result == {"db": {"host": "localhost", "port": 5432}}


def test_nested_dict_deep_3_levels():
    with pytest.raises(ValueError, match="a.b.c: expected int"):
        validate(
            {"a": {"b": {"c": int}}},
            {"a": {"b": {"c": "bad"}}},
        )


def test_nested_dict_missing_key():
    with pytest.raises(
        ValueError, match="db.host: missing required key"
    ):
        validate(
            {"db": {"host": str, "port": int}},
            {"db": {"port": 5432}},
        )


def test_nested_dict_extra_keys_stripped():
    result = validate(
        {"db": {"host": str}},
        {"db": {"host": "x", "extra": 1}},
        unknown_keys="strip",
    )
    assert result == {"db": {"host": "x"}}
    assert "extra" not in result["db"]


def test_bare_dict_type_backward_compat():
    result = validate({"x": dict}, {"x": {"a": 1}})
    assert result == {"x": {"a": 1}}


def test_nested_dict_empty_schema():
    result = validate(
        {"db": {}}, {"db": {"a": 1}}, unknown_keys="strip"
    )
    assert result == {"db": {}}


def test_nested_dict_value_is_none():
    with pytest.raises(
        ValueError, match="db: expected dict, got NoneType"
    ):
        validate({"db": {"host": str}}, {"db": None})


# --- validate: list element typing ---

def test_list_element_happy_path():
    result = validate({"tags": [str]}, {"tags": ["a", "b"]})
    assert result == {"tags": ["a", "b"]}


def test_list_element_type_mismatch():
    with pytest.raises(
        ValueError, match=r"tags\[1\]: expected str, got int"
    ):
        validate({"tags": [str]}, {"tags": ["a", 42]})


def test_list_value_not_a_list():
    with pytest.raises(
        ValueError, match="tags: expected list, got str"
    ):
        validate({"tags": [str]}, {"tags": "notalist"})


def test_list_element_empty_list():
    result = validate({"tags": [str]}, {"tags": []})
    assert result == {"tags": []}


def test_list_of_dicts():
    schema = {"users": [{"name": str}]}
    data = {"users": [{"name": "Alice"}, {"name": "Bob"}]}
    result = validate(schema, data)
    assert result == {
        "users": [{"name": "Alice"}, {"name": "Bob"}]
    }


def test_list_with_coercion():
    result = validate(
        {"nums": [int]},
        {"nums": ["1", "2", "3"]},
        coerce=True,
    )
    assert result == {"nums": [1, 2, 3]}


def test_bare_list_type_backward_compat():
    result = validate({"x": list}, {"x": [1, "two", 3.0]})
    assert result == {"x": [1, "two", 3.0]}


def test_list_of_dicts_with_errors():
    with pytest.raises(
        ValueError,
        match=r"users\[0\]\.name: expected str, got int",
    ):
        validate(
            {"users": [{"name": str}]},
            {"users": [{"name": 42}]},
        )


def test_list_of_dicts_with_optional_keys():
    schema = {
        "items": [{"name": str, "count": Optional(int, 0)}]
    }
    data = {"items": [{"name": "a"}, {"name": "b", "count": 5}]}
    result = validate(schema, data)
    assert result == {
        "items": [{"name": "a", "count": 0},
                  {"name": "b", "count": 5}]
    }


def test_list_value_is_none():
    with pytest.raises(
        ValueError, match="tags: expected list, got NoneType"
    ):
        validate({"tags": [str]}, {"tags": None})


def test_list_of_lists():
    schema = {"matrix": [[int]]}
    data = {"matrix": [[1, 2], [3, 4]]}
    assert validate(schema, data) == {
        "matrix": [[1, 2], [3, 4]]
    }


def test_list_of_lists_inner_error():
    with pytest.raises(
        ValueError,
        match=r"matrix\[0\]\[1\]: expected int, got str",
    ):
        validate(
            {"matrix": [[int]]},
            {"matrix": [[1, "bad"]]},
        )


def test_list_float_coercion_failure():
    with pytest.raises(
        ValueError,
        match=r"nums\[0\]: cannot coerce 'notanumber' to float",
    ):
        validate(
            {"nums": [float]},
            {"nums": ["notanumber"]},
            coerce=True,
        )


# --- validate: optional keys ---

def test_optional_with_default_missing():
    result = validate({"port": Optional(int, 8080)}, {})
    assert result == {"port": 8080}


def test_optional_with_default_present():
    result = validate(
        {"port": Optional(int, 8080)}, {"port": 3000}
    )
    assert result == {"port": 3000}


def test_optional_no_default_missing():
    result = validate({"debug": Optional(bool)}, {})
    assert result == {}


def test_optional_with_coercion():
    result = validate(
        {"port": Optional(int, 8080)},
        {"port": "3000"},
        coerce=True,
    )
    assert result == {"port": 3000}


def test_optional_none_default():
    result = validate({"port": Optional(int, None)}, {})
    assert result == {"port": None}


def test_optional_wrong_type_no_coerce():
    with pytest.raises(ValueError, match="port: expected int"):
        validate({"port": Optional(int)}, {"port": "abc"})


def test_optional_wrong_type_coerce_fails():
    with pytest.raises(
        ValueError, match="port: cannot coerce 'abc' to int"
    ):
        validate(
            {"port": Optional(int)},
            {"port": "abc"},
            coerce=True,
        )


def test_optional_nested_dict():
    result = validate(
        {"db": Optional({"host": str}, {})}, {}
    )
    assert result == {"db": {}}


def test_optional_list():
    result = validate({"tags": Optional([str], [])}, {})
    assert result == {"tags": []}


def test_optional_mixed_required_and_optional():
    with pytest.raises(
        ValueError, match="name: missing required key"
    ):
        validate(
            {"name": str, "port": Optional(int, 8080)}, {}
        )


# --- validate: sprint 0 review findings ---

def test_float_coercion_failure():
    with pytest.raises(
        ValueError,
        match="cannot coerce 'notanumber' to float",
    ):
        validate(
            {"x": float}, {"x": "notanumber"}, coerce=True
        )


def test_coerce_false_container_type_mismatch_list():
    with pytest.raises(
        ValueError, match="expected list, got str"
    ):
        validate({"x": list}, {"x": "notalist"})


def test_coerce_false_container_type_mismatch_dict():
    with pytest.raises(
        ValueError, match="expected dict, got str"
    ):
        validate({"x": dict}, {"x": "notadict"})


def test_invalid_schema_value_int():
    with pytest.raises(
        TypeError, match="invalid schema value"
    ):
        validate({"x": 42}, {"x": 1})


def test_invalid_schema_value_list_len_2():
    with pytest.raises(
        TypeError, match="list schema must contain exactly one"
    ):
        validate({"x": [str, int]}, {"x": ["a"]})


def test_invalid_schema_value_empty_list():
    with pytest.raises(
        TypeError, match="list schema must contain exactly one"
    ):
        validate({"x": []}, {"x": ["a"]})


def test_double_wrapped_optional():
    with pytest.raises(
        TypeError, match="invalid schema value"
    ):
        validate({"x": Optional(Optional(int))}, {"x": 1})


def test_optional_invalid_type_int():
    with pytest.raises(
        TypeError, match="invalid schema value"
    ):
        validate({"x": Optional(42)}, {"x": 1})


def test_optional_invalid_type_str():
    with pytest.raises(
        TypeError, match="invalid schema value"
    ):
        validate({"x": Optional("str")}, {"x": "a"})


# --- validate: combination tests (code review findings) ---

def test_coerce_nested_dict_with_list():
    result = validate(
        {"db": {"ports": [int]}},
        {"db": {"ports": ["1", "2"]}},
        coerce=True,
    )
    assert result == {"db": {"ports": [1, 2]}}


def test_large_list_1000_elements():
    schema = {"tags": [int]}
    data = {"tags": list(range(1000))}
    result = validate(schema, data)
    assert result == {"tags": list(range(1000))}


def test_optional_nested_dict_with_coercion():
    result = validate(
        {"db": Optional({"port": int}, {})},
        {"db": {"port": "5432"}},
        coerce=True,
    )
    assert result == {"db": {"port": 5432}}


# --- validate: multi-level error aggregation ---

def test_multi_level_error_aggregation():
    schema = {
        "name": str,
        "db": {"port": int},
        "tags": [str],
    }
    data = {
        "db": {"port": "bad"},
        "tags": ["ok", 42],
    }
    with pytest.raises(ValueError) as exc:
        validate(schema, data)
    msg = str(exc.value)
    assert "name: missing required key" in msg
    assert "db.port: expected int" in msg
    assert "tags[1]: expected str, got int" in msg
