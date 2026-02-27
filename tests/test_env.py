"""Tests for zodify env() function."""

import pytest
from zodify import env


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


def test_env_float_empty_string(monkeypatch):
    monkeypatch.setenv("X", "")
    with pytest.raises(
        ValueError,
        match="cannot coerce empty string to float",
    ):
        env("X", float)


def test_env_bool_empty_string(monkeypatch):
    monkeypatch.setenv("X", "")
    with pytest.raises(
        ValueError,
        match="cannot coerce empty string to bool",
    ):
        env("X", bool)
