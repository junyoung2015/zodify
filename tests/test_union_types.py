"""Tests for union type validation"""

import ast
import inspect
import textwrap

import pytest
import zodify

from zodify import Optional, validate


def _get_check_value_function_ast() -> ast.FunctionDef:
    """Return parsed AST for zodify._check_value."""
    source = textwrap.dedent(inspect.getsource(zodify._check_value))
    module = ast.parse(source)
    func = module.body[0]
    assert isinstance(func, ast.FunctionDef)
    return func


def _get_check_value_if_conditions() -> list[str]:
    """Return top-level if-condition expressions from _check_value."""
    func = _get_check_value_function_ast()
    return [ast.unparse(stmt.test) for stmt in func.body if isinstance(stmt, ast.If)]


# --- Basic union matching (AC: #1, #2, #5) ---


def test_validate_union_str_matches_first_type() -> None:
    """{"value": str | int} with "hello" → passes"""
    result = validate({"value": str | int}, {"value": "hello"})
    assert result == {"value": "hello"}


def test_validate_union_int_matches_second_type() -> None:
    """{"value": str | int} with 42 → passes"""
    result = validate({"value": str | int}, {"value": 42})
    assert result == {"value": 42}


def test_validate_union_bool_matches_bool_type() -> None:
    """{"value": bool | str} with True → matches bool (type(True) is bool, not int)"""
    result = validate({"value": bool | str}, {"value": True})
    assert result == {"value": True}


# --- Union mismatch (AC: #3, #8) ---


def test_validate_union_mismatch_error() -> None:
    """{"value": str | int} with 3.14 → error"""
    with pytest.raises(ValueError, match="expected str | int, got float"):
        validate({"value": str | int}, {"value": 3.14})


def test_validate_union_error_message_format() -> None:
    """Verify error message string: "value: expected str | int, got float" """
    with pytest.raises(ValueError) as exc_info:
        validate({"value": str | int}, {"value": 3.14})
    assert str(exc_info.value) == "value: expected str | int, got float"


def test_validate_union_error_tuple_contract_fields() -> None:
    """Directly verify the 4-tuple fields (path, msg, expected, got) for union mismatch."""
    errors: list[tuple[str, str, str, str]] = []
    zodify._check_value(3.14, str | int, "value", False, errors, 32, "reject")
    assert errors == [("value", "expected str | int, got float", "str | int", "float")]


# --- Three-or-more types (AC: #6) ---


def test_validate_union_three_types_match() -> None:
    """{"value": str | int | float} with 3.14 → passes (float matches)"""
    result = validate({"value": str | int | float}, {"value": 3.14})
    assert result == {"value": 3.14}


def test_validate_union_three_types_mismatch() -> None:
    """{"value": str | int | float} with True → error (bool is not str/int/float by exact check)"""
    with pytest.raises(ValueError, match="expected str | int | float, got bool"):
        validate({"value": str | int | float}, {"value": True})


# --- Args order (AC: #5) ---


def test_validate_union_first_exact_match_wins() -> None:
    """Verify union branch iterates __args__ and returns on first exact match."""
    func = _get_check_value_function_ast()
    union_branch = next(
        stmt for stmt in func.body
        if isinstance(stmt, ast.If)
        and ast.unparse(stmt.test) == "isinstance(expected, types.UnionType)"
    )

    assert isinstance(union_branch.body[0], ast.For)
    union_loop = union_branch.body[0]
    assert ast.unparse(union_loop.iter) == "expected.__args__"
    assert isinstance(union_loop.body[0], ast.If)
    match_check = union_loop.body[0]
    assert ast.unparse(match_check.test) == "type(value) is t and (not coerce or t is not str)"
    assert any(isinstance(stmt, ast.Return) and ast.unparse(stmt.value) == "value"
               for stmt in match_check.body)


def test_validate_union_dispatch_position_regression() -> None:
    """Verify union dispatch position is before type(expected) is type."""
    conditions = _get_check_value_if_conditions()
    assert conditions[:5] == [
        "isinstance(expected, dict)",
        "isinstance(expected, list) and len(expected) == 1",
        "isinstance(expected, list)",
        "isinstance(expected, types.UnionType)",
        "type(expected) is type",
    ]


# --- Union + Optional (AC: #7) ---


def test_validate_union_with_optional_default_applied() -> None:
    """Optional(str | int, default=0) with missing key → default 0"""
    result = validate({"value": Optional(str | int, default=0)}, {})
    assert result == {"value": 0}


def test_validate_union_with_optional_present_validates() -> None:
    """Optional(str | int) with present key → union validation runs"""
    result = validate({"value": Optional(str | int)}, {"value": "hello"})
    assert result == {"value": "hello"}


# --- Union in list (AC: #9) ---


def test_validate_union_in_list_valid_items() -> None:
    """{"items": [str | int]} with ["hello", 42] → passes"""
    result = validate({"items": [str | int]}, {"items": ["hello", 42]})
    assert result == {"items": ["hello", 42]}


def test_validate_union_in_list_mismatch_error() -> None:
    """{"items": [str | int]} with ["hello", 42, 3.14] → items[2] error"""
    with pytest.raises(ValueError, match=r"items\[2\]: expected str \| int, got float"):
        validate({"items": [str | int]}, {"items": ["hello", 42, 3.14]})


# --- Union in nested dict (regression guard) ---


def test_validate_union_in_nested_dict_valid() -> None:
    """{"config": {"value": str | int}} with nested "hello" → passes via dict recursion"""
    result = validate(
        {"config": {"value": str | int}},
        {"config": {"value": "hello"}},
    )
    assert result == {"config": {"value": "hello"}}


# --- Union coercion order-sensitive tests ---


def test_validate_union_coerce_str_int_str_value_returns_str() -> None:
    """str | int + "42" + coerce=True → str coercion returns "42" (str first)."""
    result = validate({"value": str | int}, {"value": "42"}, coerce=True)
    assert result == {"value": "42"}


def test_validate_union_coerce_int_str_str_value_returns_int() -> None:
    """int | str + "42" + coerce=True → int coercion returns 42 (int first)."""
    result = validate({"value": int | str}, {"value": "42"}, coerce=True)
    assert result == {"value": 42}


def test_validate_union_coerce_int_float_abc_raises() -> None:
    """int | float + "abc" + coerce=True → all fail → error."""
    with pytest.raises(ValueError, match="expected int | float, got str"):
        validate({"value": int | float}, {"value": "abc"}, coerce=True)


# --- Two-pass behavior test (AC: 4) ---


def test_validate_union_coerce_exact_match_before_coercion() -> None:
    """str | int with 42 (int) + coerce=True → Pass 1 exact match returns 42."""
    result = validate({"value": str | int}, {"value": 42}, coerce=True)
    assert result == {"value": 42}
    assert type(result["value"]) is int


# --- Union coercion tuple contract (AC: 3, 5) ---


def test_validate_union_coerce_miss_tuple_contract() -> None:
    """Verify 4-tuple error fields for union coercion miss."""
    errors: list[tuple[str, str, str, str]] = []
    zodify._check_value("abc", int | float, "value", True, errors, 32, "reject")
    assert errors == [("value", "expected int | float, got str", "int | float", "str")]


# --- Known limitation: str catch-all coercion (AC: 5) ---


def test_validate_union_coerce_int_str_bool_falls_through_to_str() -> None:
    """int | str with True + coerce=True → bool doesn't match int or str exactly,
    coercion falls through to str(True) == "True"."""
    result = validate({"value": int | str}, {"value": True}, coerce=True)
    assert result == {"value": "True"}
    assert type(result["value"]) is str


# --- Composite scenario tests (nested/list/Optional + union coercion) ---


def test_validate_union_coerce_in_list() -> None:
    """{"items": [int | str]} with ["42"] + coerce=True → [42]."""
    result = validate({"items": [int | str]}, {"items": ["42"]}, coerce=True)
    assert result == {"items": [42]}


def test_validate_union_coerce_in_nested_dict() -> None:
    """{"config": {"v": int | str}} with {"v": "42"} + coerce=True → coerced."""
    result = validate(
        {"config": {"v": int | str}},
        {"config": {"v": "42"}},
        coerce=True,
    )
    assert result == {"config": {"v": 42}}


def test_validate_union_coerce_with_optional_present() -> None:
    """Optional(int | str) with "42" + coerce=True → 42."""
    result = validate(
        {"value": Optional(int | str)}, {"value": "42"}, coerce=True,
    )
    assert result == {"value": 42}


# --- Non-string-to-non-string edge case ---


def test_validate_union_coerce_float_int_bool_rejects() -> None:
    """float | int with True (bool) + coerce=True → all fail (non-str input
    rejected by _coerce_value for non-str targets) → error."""
    with pytest.raises(ValueError, match="expected float | int, got bool"):
        validate({"value": float | int}, {"value": True}, coerce=True)


# --- coerce=False regression guard ---


def test_validate_union_coerce_false_no_coercion() -> None:
    """int | float + "42" + coerce=False → error (no coercion attempted)."""
    with pytest.raises(ValueError, match="expected int | float, got str"):
        validate({"value": int | float}, {"value": "42"}, coerce=False)


# --- str catch-all coercion edge cases (adversarial review) ---


def test_validate_union_coerce_str_int_float_to_str_catchall() -> None:
    """str | int with 3.14 (float) + coerce=True → str catch-all produces "3.14"."""
    result = validate({"value": str | int}, {"value": 3.14}, coerce=True)
    assert result == {"value": "3.14"}
    assert type(result["value"]) is str


def test_validate_union_coerce_str_int_none_to_str_catchall() -> None:
    """str | int with None + coerce=True → str catch-all produces "None"."""
    result = validate({"value": str | int}, {"value": None}, coerce=True)
    assert result == {"value": "None"}
    assert type(result["value"]) is str


def test_validate_union_coerce_bool_int_str_coercion() -> None:
    """bool | int with "true" + coerce=True → bool coercion succeeds first."""
    result = validate({"value": bool | int}, {"value": "true"}, coerce=True)
    assert result == {"value": True}
    assert type(result["value"]) is bool


# --- Path-verification: str exact-match suppression (adversarial review) ---


def test_validate_union_coerce_str_suppressed_in_pass1(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify str exact-match is suppressed in Pass 1 when coerce=True.
    str | int with "42" + coerce=True must reach _coerce_value (Pass 2),
    NOT return via Pass 1 exact-match."""
    calls: list[tuple[str, type]] = []
    original_coerce = zodify._coerce_value

    def tracking_coerce(value: object, target: type, key: str) -> object:
        calls.append((str(value), target))
        return original_coerce(value, target, key)

    monkeypatch.setattr(zodify, "_coerce_value", tracking_coerce)
    result = validate({"value": str | int}, {"value": "42"}, coerce=True)
    assert result == {"value": "42"}
    # _coerce_value MUST have been called (proving Pass 1 did NOT exact-match str)
    assert len(calls) > 0, "_coerce_value was never called — str exact-match was not suppressed"
    assert ("42", str) in calls, "Expected _coerce_value('42', str, ...) call in Pass 2"


def test_validate_union_no_coerce_str_exact_match_no_coercion(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify str exact-match works in Pass 1 when coerce=False (no suppression).
    str | int with "42" + coerce=False must NOT call _coerce_value."""
    calls: list[tuple[str, type]] = []
    original_coerce = zodify._coerce_value

    def tracking_coerce(value: object, target: type, key: str) -> object:
        calls.append((str(value), target))
        return original_coerce(value, target, key)

    monkeypatch.setattr(zodify, "_coerce_value", tracking_coerce)
    result = validate({"value": str | int}, {"value": "42"}, coerce=False)
    assert result == {"value": "42"}
    assert len(calls) == 0, "_coerce_value was called — str should exact-match in Pass 1 when coerce=False"
