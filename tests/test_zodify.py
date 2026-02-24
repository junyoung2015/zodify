"""Tests for zodify (zodify)."""

import pytest
from zodify import (
    count_in_list, validate, env, __version__,
)


# --- __version__ ---

def test_version():
    assert __version__ == "0.0.1"


# --- count_in_list ---

def test_count_in_list_found():
    assert count_in_list(["toto", "tata", "toto"], "toto") == 2


def test_count_in_list_not_found():
    assert count_in_list(["toto", "tata", "toto"], "tutu") == 0


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
    assert validate({"a": int}, {"a": 1, "b": 2}) == {"a": 1}


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
    assert validate({}, {"a": 1}) == {}
    assert validate({}, {}) == {}


def test_validate_none_value():
    with pytest.raises(ValueError, match="expected str"):
        validate({"a": str}, {"a": None})


# --- env ---

def test_env_reads_int(monkeypatch):
    monkeypatch.setenv("TEST_PORT", "3000")
    assert env("TEST_PORT", int) == 3000


def test_env_default():
    assert env("NONEXISTENT_ZZZ", str, default="fallback") == "fallback"


def test_env_default_none():
    assert env("NONEXISTENT_ZZZ", str, default=None) is None


def test_env_missing_required():
    with pytest.raises(ValueError, match="missing required"):
        env("NONEXISTENT_ZZZ", str)


def test_env_bool_case_insensitive(monkeypatch):
    monkeypatch.setenv("TEST_DEBUG", "YES")
    assert env("TEST_DEBUG", bool) is True
    monkeypatch.setenv("TEST_DEBUG", "no")
    assert env("TEST_DEBUG", bool) is False


def test_env_str_passthrough(monkeypatch):
    monkeypatch.setenv("TEST_NAME", "myapp")
    assert env("TEST_NAME", str) == "myapp"


def test_env_float(monkeypatch):
    monkeypatch.setenv("TEST_RATE", "3.14")
    assert env("TEST_RATE", float) == pytest.approx(3.14)


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


def test_validate_empty_schema_empty_data():
    assert validate({}, {}) == {}


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


# --- env: edge cases ---

def test_env_empty_string_name():
    with pytest.raises(ValueError, match="missing required env var"):
        env("", str)


def test_env_var_set_to_empty_string_str(monkeypatch):
    monkeypatch.setenv("TEST_EMPTY", "")
    assert env("TEST_EMPTY", str) == ""


def test_env_var_set_to_empty_string_int_fails(monkeypatch):
    monkeypatch.setenv("TEST_EMPTY", "")
    with pytest.raises(ValueError, match="cannot coerce empty string"):
        env("TEST_EMPTY", int)


def test_env_overwrite(monkeypatch):
    monkeypatch.setenv("TEST_OW", "first")
    assert env("TEST_OW", str) == "first"
    monkeypatch.setenv("TEST_OW", "second")
    assert env("TEST_OW", str) == "second"


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
