"""Executable baseline for ownership, lazy schema checks, and trusted callbacks."""

import pytest

from zodify import Optional, validate


def test_defaults_are_trusted_references_and_rebinding_is_live():
    calls = []
    default = []
    marker = Optional(lambda value: calls.append(value) or False, default)
    schema = {"items": marker}
    first = validate(schema, {})
    assert first["items"] is default
    default.append("unvalidated")
    assert validate(schema, {})["items"] is first["items"]
    marker.default = "replacement"
    assert validate(schema, {}) == {"items": "replacement"}
    assert calls == []


def test_output_copies_structural_containers_but_retains_bare_values():
    bare = {"secret": []}
    item = object()
    data = {"nested": {"bare": bare}, "items": [item]}
    result = validate({"nested": {"bare": dict}, "items": [object]}, data)
    assert result is not data
    assert result["nested"] is not data["nested"]
    assert result["nested"]["bare"] is bare
    assert result["items"] is not data["items"]
    assert result["items"][0] is item


@pytest.mark.parametrize("mode", ["text", "structured"])
def test_callbacks_run_once_in_order_after_earlier_failure_and_can_mutate(mode):
    calls = []
    data = {"bad": "wrong", "first": [], "second": 1}

    def first(value):
        calls.append("first")
        value.append("mutated")
        data["second"] = 2
        return [True]  # Predicate result uses truthiness, not exact bool.

    def second(value):
        calls.append(("second", value))
        return False

    with pytest.raises(ValueError):
        validate({"bad": int, "first": first, "second": second}, data, error_mode=mode)
    assert calls == ["first", ("second", 2)]
    assert data["first"] == ["mutated"]


def test_missing_invalid_rule_remains_lazy_and_default_bypasses_it():
    with pytest.raises(ValueError, match="missing required key"):
        validate({"bad": []}, {})
    with pytest.raises(TypeError, match="list schema must contain"):
        validate({"bad": []}, {"bad": []})
    assert validate({"bad": Optional([], "trusted")}, {}) == {"bad": "trusted"}


def test_list_depth_is_not_dictionary_depth_and_bare_container_is_opaque():
    assert validate({"items": [[[int]]]}, {"items": [[[1]]]}, max_depth=1)
    with pytest.raises(ValueError, match="max depth exceeded"):
        validate({"items": [{"v": int}]}, {"items": [{"v": 1}]}, max_depth=1)
    cyclic = {}
    cyclic["self"] = cyclic
    assert validate({"opaque": dict}, {"opaque": cyclic}, max_depth=1)["opaque"] is cyclic


@pytest.mark.parametrize("key", ["a.b", "x[0]", "", 1, ("legacy",)])
def test_unusual_dictionary_keys_keep_runtime_acceptance(key):
    assert validate({key: int}, {key: 1}) == {key: 1}


@pytest.mark.parametrize("coerce", [False, True])
@pytest.mark.parametrize("rule", [int | str, str | int])
@pytest.mark.parametrize("value", [42, "42", True, "true", None, ""])
def test_union_matrix_preserves_exact_match_and_string_member_order(rule, value, coerce):
    if not coerce and type(value) not in (int, str):
        with pytest.raises(ValueError):
            validate({"v": rule}, {"v": value}, coerce=coerce)
        return
    expected = value
    if coerce and type(value) is not int:
        expected = 42 if rule.__args__[0] is int and value == "42" else str(value)
    result = validate({"v": rule}, {"v": value}, coerce=coerce)["v"]
    assert result == expected
    assert type(result) is type(expected)


def test_reentrant_callback_has_independent_execution_state():
    def callback(value):
        assert validate({"inner": int}, {"inner": value}) == {"inner": value}
        return True

    assert validate({"outer": callback}, {"outer": 1}) == {"outer": 1}


def test_exact_types_reject_subclasses_without_constructor_widening():
    class SubInt(int):
        pass

    for value in [True, 1.0, SubInt(1)]:
        with pytest.raises(ValueError, match="expected int"):
            validate({"v": int}, {"v": value})
    with pytest.raises(ValueError, match="expected float"):
        validate({"v": float}, {"v": 1}, coerce=True)


def test_callback_truthiness_exceptions_are_validation_failures_but_baseexceptions_escape():
    class Ambiguous:
        def __bool__(self):
            raise ValueError("ambiguous predicate result")

    with pytest.raises(ValueError, match="custom validation failed.*ambiguous"):
        validate({"v": lambda _: Ambiguous()}, {"v": 1})

    def interrupt(_):
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        validate({"v": interrupt}, {"v": 1})


def test_list_callback_observes_live_appended_input_items():
    data = {"items": [1]}
    calls = []

    def visit(value):
        calls.append(value)
        if value == 1:
            data["items"].append(2)
        return True

    assert validate({"items": [visit]}, data) == {"items": [1, 2]}
    assert calls == [1, 2]
