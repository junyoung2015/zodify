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
