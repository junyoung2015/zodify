"""Canonical failures preserve legacy errors without retaining raw values."""

import copy
import pickle
from typing import get_type_hints

import pytest

from zodify import ValidationError, ValidationIssue, Validator, load_env, validate


def failure(schema, data, **kwargs):
    with pytest.raises(ValidationError) as caught:
        validate(schema, data, error_mode="structured", **kwargs)
    return caught.value


def test_locations_distinguish_legacy_path_collisions():
    error = failure(
        {"a.b": int, "a": {"b": int}, "x[0]": int, "x": [int], "": {"": int}},
        {"a.b": "s", "a": {"b": "s"}, "x[0]": "s", "x": ["s"], "": {"": "s"}},
    )
    assert [issue.loc for issue in error.details] == [
        ("a.b",), ("a", "b"), ("x[0]",), ("x", 0), ("", ""),
    ]
    assert [issue.path for issue in error.details] == ["a.b", "a.b", "x[0]", "x[0]", "."]
    assert all(set(issue) == {"path", "message", "expected", "got"} for issue in error.issues)


def test_machine_categories_follow_traversal_order():
    error = failure(
        {"missing": int, "bad": [int], "union": int | float, "callback": lambda x: False,
         "deep": {"field": int}},
        {"bad": ["secret"], "union": True, "callback": "secret", "deep": {"field": 1}, "extra": 1},
        coerce=True, max_depth=1,
    )
    assert [issue.code for issue in error.details] == [
        "missing_key", "coercion_failed", "union_mismatch", "custom_validation_failed",
        "depth_exceeded", "unknown_key",
    ]
    assert [issue.loc for issue in error.details] == [
        ("missing",), ("bad", 0), ("union",), ("callback",), ("deep",), ("extra",),
    ]
    assert failure({"v": int}, {"v": True}).details[0].code == "type_mismatch"
    assert failure({"v": [int]}, {"v": 1}).details[0].code == "type_mismatch"
    assert failure({"v": {}}, {"v": 1}).details[0].code == "type_mismatch"
    assert failure({}, {}, max_depth=0).details[0].loc == ()


def test_value_free_details_do_not_change_legacy_coercion_or_callback_text():
    calls = []

    def callback(value):
        calls.append(value)
        raise RuntimeError("CALLBACK_SECRET")

    error = failure({"VALUE_SECRET": int, "callback": callback},
                    {"VALUE_SECRET": "INPUT_SECRET", "callback": "INPUT_SECRET"}, coerce=True)
    assert calls == ["INPUT_SECRET"]
    assert "INPUT_SECRET" in str(error)
    assert "CALLBACK_SECRET" in str(error)
    assert "INPUT_SECRET" not in repr(error.details)
    assert "CALLBACK_SECRET" not in repr(error.details)
    # Field names remain application data: no claim of universal logging safety.
    assert "VALUE_SECRET" in repr(error.details)


def test_immutable_detail_snapshot_is_independent_of_mutable_legacy_issues():
    error = failure({"v": int}, {"v": "wrong"})
    snapshot = error.details
    error.issues[0]["path"] = "changed"
    error.issues.clear()
    assert error.details is snapshot
    assert snapshot[0].loc == ("v",)
    with pytest.raises(AttributeError):
        snapshot[0].code = "changed"
    with pytest.raises(TypeError):
        snapshot[0].loc[0] = "changed"


@pytest.mark.parametrize("clone", [copy.copy, copy.deepcopy, lambda e: pickle.loads(pickle.dumps(e))])
def test_exception_copy_and_pickle_preserve_both_views(clone):
    error = failure({"v": [int]}, {"v": ["wrong"]})
    copied = clone(error)
    assert type(copied) is ValidationError
    assert copied.issues == error.issues
    assert copied.issues is not error.issues
    assert copied.details == error.details
    assert str(copied) == str(error)
    assert isinstance(copied, ValueError)


@pytest.mark.parametrize("clone", [copy.copy, copy.deepcopy, lambda e: pickle.loads(pickle.dumps(e))])
def test_manual_constructor_keeps_arbitrary_legacy_keys_and_no_details(clone):
    error = ValidationError([{"path": "a.b", "message": "legacy", "extension": "ok"}])
    assert error.details is None
    assert clone(error).details is None
    assert clone(error).issues == error.issues
    with pytest.raises(KeyError):
        ValidationError([{"path": "missing message"}])


def test_parser_errors_have_no_fabricated_locations(tmp_path):
    file = tmp_path / ".env"
    file.write_text("invalid line\n")
    with pytest.raises(ValidationError) as caught:
        load_env(file, error_mode="structured")
    assert caught.value.details is None


def test_env_schema_and_validator_share_canonical_engine(tmp_path):
    file = tmp_path / ".env"
    file.write_text("PORT=bad\n")
    with pytest.raises(ValidationError) as caught:
        load_env(file, schema={"PORT": int}, error_mode="structured")
    assert caught.value.details[0].loc == ("PORT",)
    with pytest.raises(ValidationError) as caught:
        Validator(error_mode="structured").validate({"v": int}, {"v": "bad"})
    assert caught.value.details[0].loc == ("v",)


@pytest.mark.parametrize("key", [("legacy",), object(), True])
def test_unsupported_key_types_keep_legacy_failure_without_lossy_details(key):
    error = failure({key: int}, {key: "wrong"})
    assert error.details is None
    assert error.issues[0]["path"] == str(key)


def test_integer_key_is_distinct_from_string_key():
    error = failure({1: int, "1": int}, {1: "wrong", "1": "wrong"})
    assert [issue.loc for issue in error.details] == [(1,), ("1",)]


@pytest.mark.parametrize("mode", ["text", "structured"])
def test_unsupported_key_does_not_gain_extra_formatting_calls(mode):
    calls = []

    class Key:
        def __str__(self):
            calls.append("format")
            return "key"

    key = Key()
    with pytest.raises(ValueError):
        validate({key: int}, {key: "wrong"}, error_mode=mode)
    assert calls == ["format"]


def test_text_mode_remains_plain_value_error_and_public_annotations_are_typed():
    with pytest.raises(ValueError) as caught:
        validate({"v": int}, {"v": "wrong"})
    assert type(caught.value) is ValueError
    assert get_type_hints(ValidationError)["details"] == tuple[ValidationIssue, ...] | None
    assert get_type_hints(ValidationIssue)["loc"] == tuple[str | int, ...]


def test_schema_class_frontend_reports_same_canonical_locations():
    from zodify import Schema

    class Child(Schema):
        age: int

    class Parent(Schema):
        children: list[Child]

    plain = failure({"children": [{"age": int}]}, {"children": [{"age": "bad"}]})
    wrapped = failure(Parent, {"children": [{"age": "bad"}]})
    assert wrapped.details == plain.details
    assert wrapped.issues == plain.issues
