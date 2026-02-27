"""Tests for unknown key handling."""

import pytest
import zodify
from zodify import validate, Optional


def test_unknown_keys_reject_default():
    with pytest.raises(ValueError, match="age: unknown key"):
        validate({"name": str}, {"name": "kai", "age": 25})


def test_unknown_keys_reject_explicit():
    with pytest.raises(ValueError, match="age: unknown key"):
        validate(
            {"name": str},
            {"name": "kai", "age": 25},
            unknown_keys="reject",
        )


def test_unknown_keys_strip():
    result = validate(
        {"name": str},
        {"name": "kai", "age": 25},
        unknown_keys="strip",
    )
    assert result == {"name": "kai"}


def test_unknown_keys_invalid_value_raises():
    with pytest.raises(ValueError, match="unknown_keys must be 'reject' or 'strip'"):
        validate(
            {"name": str},
            {"name": "kai"},
            unknown_keys="allow",
        )


def test_unknown_keys_no_extra_keys_passes():
    assert validate({"name": str}, {"name": "kai"}) == {"name": "kai"}


def test_unknown_keys_nested_reject():
    with pytest.raises(ValueError, match="user.extra: unknown key"):
        validate(
            {"user": {"name": str}},
            {"user": {"name": "kai", "extra": 1}},
        )


def test_unknown_keys_nested_strip():
    result = validate(
        {"user": {"name": str}},
        {"user": {"name": "kai", "extra": 1}},
        unknown_keys="strip",
    )
    assert result == {"user": {"name": "kai"}}


def test_unknown_keys_list_of_dicts_reject():
    with pytest.raises(
        ValueError, match=r"users\[0\]\.age: unknown key"
    ):
        validate(
            {"users": [{"name": str}]},
            {"users": [{"name": "kai", "age": 25}]},
        )


def test_unknown_keys_list_of_dicts_strip():
    result = validate(
        {"users": [{"name": str}]},
        {"users": [{"name": "kai", "age": 25}]},
        unknown_keys="strip",
    )
    assert result == {"users": [{"name": "kai"}]}


def test_unknown_keys_optional_not_flagged():
    result = validate(
        {"name": str, "port": Optional(int, 8080)},
        {"name": "kai"},
    )
    assert result == {"name": "kai", "port": 8080}


def test_unknown_keys_multiple_unknown():
    with pytest.raises(ValueError) as exc_info:
        validate(
            {"name": str},
            {"name": "kai", "age": 25, "team": "red"},
        )
    msg = str(exc_info.value)
    assert "age: unknown key" in msg
    assert "team: unknown key" in msg


def test_unknown_keys_error_tuple_format():
    with pytest.raises(ValueError) as exc_info:
        validate({"name": str}, {"name": "kai", "extra": 1})
    assert str(exc_info.value) == "extra: unknown key"


def test_unknown_keys_error_tuple_contract_fields():
    errors = []
    result = zodify._validate(
        {"name": str},
        {"name": "kai", "extra": 1},
        False,
        "",
        errors,
        32,
        "reject",
    )
    assert result == {"name": "kai"}
    assert errors == [("extra", "unknown key", "known", "unknown")]


def test_unknown_keys_deep_nested_reject():
    with pytest.raises(ValueError, match=r"a\.b\.extra: unknown key"):
        validate(
            {"a": {"b": {"c": str}}},
            {"a": {"b": {"c": "ok", "extra": 1}}},
        )


def test_unknown_keys_depth_exceeded_no_unknown_error():
    with pytest.raises(ValueError) as exc_info:
        validate(
            {"a": {"b": str}},
            {"a": {"b": "x", "extra": 1}},
            max_depth=1,
            unknown_keys="reject",
        )
    msg = str(exc_info.value)
    assert msg == "a: max depth exceeded"
    assert "unknown key" not in msg
