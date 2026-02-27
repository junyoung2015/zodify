"""Tests for recursion depth limit."""

import pytest
import zodify
from zodify import validate, Optional


def _make_deep(n):
    """Build n-level nested schema and matching data."""
    schema = {"value": int}
    data = {"value": 1}
    for _ in range(n):
        schema = {"nested": schema}
        data = {"nested": data}
    return schema, data


def test_depth_default_flat_passes():
    """Flat dict with default max_depth=32 passes transparently."""
    result = validate({"name": str}, {"name": "hello"})
    assert result == {"name": "hello"}


def test_depth_default_boundary_passes():
    """_make_deep(31) passes with default max_depth=32."""
    schema, data = _make_deep(31)
    result = validate(schema, data)
    # Walk down 31 levels to find the leaf value
    node = result
    for _ in range(31):
        node = node["nested"]
    assert node == {"value": 1}


def test_depth_default_boundary_fails():
    """_make_deep(32) fails with default max_depth=32."""
    schema, data = _make_deep(32)
    expected_path = ".".join(["nested"] * 32)
    expected_msg = f"{expected_path}: max depth exceeded"
    with pytest.raises(ValueError) as exc_info:
        validate(schema, data)
    assert str(exc_info.value) == expected_msg


def test_depth_custom_limit():
    """max_depth=3 — _make_deep(2) passes, _make_deep(3) fails."""
    schema_ok, data_ok = _make_deep(2)
    result = validate(schema_ok, data_ok, max_depth=3)
    assert result["nested"]["nested"] == {"value": 1}

    schema_fail, data_fail = _make_deep(3)
    with pytest.raises(ValueError, match="max depth exceeded"):
        validate(schema_fail, data_fail, max_depth=3)


def test_depth_one_flat_passes():
    """max_depth=1 — flat dict passes."""
    result = validate({"a": int}, {"a": 42}, max_depth=1)
    assert result == {"a": 42}


def test_depth_one_nested_fails():
    """max_depth=1 — nested dict fails with exact path."""
    with pytest.raises(ValueError, match="db: max depth exceeded"):
        validate({"db": {"host": str}}, {"db": {"host": "x"}}, max_depth=1)


def test_depth_zero_immediate_error():
    """max_depth=0 — any dict immediately fails."""
    with pytest.raises(ValueError, match="max depth exceeded") as exc_info:
        validate({"a": int}, {"a": 1}, max_depth=0)
    assert exc_info.value.args[0].startswith(": max depth exceeded")


def test_depth_negative_immediate_error():
    """max_depth=-1 — same as 0, immediate failure."""
    with pytest.raises(ValueError, match="max depth exceeded"):
        validate({"a": int}, {"a": 1}, max_depth=-1)


def test_depth_nested_list_no_depth_consumed():
    """List wrapping a dict does NOT consume extra depth."""
    schema = {"items": [{"name": str}]}
    data = {"items": [{"name": "a"}]}
    result = validate(schema, data, max_depth=2)
    assert result == {"items": [{"name": "a"}]}


def test_depth_error_tuple_format():
    """Verify exact error message format."""
    schema, data = _make_deep(2)
    with pytest.raises(ValueError) as exc_info:
        validate(schema, data, max_depth=2)
    assert "nested.nested: max depth exceeded" in str(exc_info.value)


def test_depth_error_tuple_contract_fields():
    """Verify depth-exceeded tuple contract expected/got fields."""
    errors = []
    result = zodify._validate(
        {"a": int}, {"a": 1}, False, "", errors, 0, "reject"
    )
    assert result == {}
    assert errors == [("", "max depth exceeded", "max_depth", "exceeded")]


def test_depth_with_optional():
    """Optional unwrap + nested dict within limit."""
    schema = {"db": Optional({"host": str}, {})}
    data = {"db": {"host": "x"}}
    result = validate(schema, data, max_depth=2)
    assert result == {"db": {"host": "x"}}


def test_depth_with_coerce():
    """Nested dict with coercion within limit."""
    schema = {"db": {"port": int}}
    data = {"db": {"port": "5432"}}
    result = validate(schema, data, max_depth=2, coerce=True)
    assert result == {"db": {"port": 5432}}
