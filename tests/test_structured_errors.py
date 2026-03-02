"""Tests for ValidationError structured issue containers."""

import copy
import pickle

import pytest

import zodify
from zodify import validate, ValidationError


def test_validationerror_is_valueerror_subclass():
    assert issubclass(ValidationError, ValueError)


def test_validationerror_is_caught_by_valueerror_except():
    with pytest.raises(ValueError):
        raise ValidationError([
            {
                "path": "db.port",
                "message": "expected int, got str",
                "expected": "int",
                "got": "str",
            }
        ])


def test_validationerror_issues_shape():
    err = ValidationError([
        {
            "path": "db.port",
            "message": "expected int, got str",
            "expected": "int",
            "got": "str",
        },
        {
            "path": "db.host",
            "message": "missing required key",
            "expected": "required",
            "got": "missing",
        },
    ])
    assert isinstance(err.issues, list)
    assert len(err.issues) == 2
    for issue in err.issues:
        assert isinstance(issue, dict)
        assert set(issue.keys()) == {"path", "message", "expected", "got"}


def test_validationerror_single_issue_str_format():
    err = ValidationError([
        {
            "path": "db.port",
            "message": "expected int, got str",
            "expected": "int",
            "got": "str",
        }
    ])
    assert str(err) == "db.port: expected int, got str"


def test_validationerror_multiple_issue_str_format():
    err = ValidationError([
        {
            "path": "db.port",
            "message": "expected int, got str",
            "expected": "int",
            "got": "str",
        },
        {
            "path": "db.host",
            "message": "expected str, got int",
            "expected": "str",
            "got": "int",
        },
    ])
    assert str(err) == (
        "db.port: expected int, got str\n"
        "db.host: expected str, got int"
    )


def test_validationerror_empty_issues_string_is_empty():
    err = ValidationError([])
    assert str(err) == ""
    assert err.issues == []


def test_validationerror_exported_from_zodify():
    from zodify import ValidationError as ImportedValidationError

    assert ImportedValidationError is ValidationError


def test_validationerror_exported_in_dunder_all():
    assert "ValidationError" in zodify.__all__


def test_validationerror_constructor_snapshot_copy_behavior():
    source_issues = [
        {
            "path": "db.port",
            "message": "expected int, got str",
            "expected": "int",
            "got": "str",
        }
    ]
    err = ValidationError(source_issues)
    before = str(err)

    source_issues.append({
        "path": "db.host",
        "message": "expected str, got int",
        "expected": "str",
        "got": "int",
    })
    source_issues[0]["message"] = "mutated"

    assert len(err.issues) == 1
    assert err.issues[0]["message"] == "expected int, got str"
    assert str(err) == before


def test_validationerror_post_construction_mutation_does_not_change_str():
    err = ValidationError([
        {
            "path": "db.port",
            "message": "expected int, got str",
            "expected": "int",
            "got": "str",
        }
    ])
    original_str = str(err)
    err.issues[0]["message"] = "tampered"
    assert str(err) == original_str


def test_validationerror_keyerror_on_malformed_issue_dict():
    with pytest.raises(KeyError):
        ValidationError([{"foo": "bar"}])


def test_validationerror_args_tuple_matches_str():
    err = ValidationError([
        {
            "path": "db.port",
            "message": "expected int, got str",
            "expected": "int",
            "got": "str",
        }
    ])
    assert err.args == (str(err),)


def test_validationerror_allows_opaque_expected_got_values():
    err = ValidationError([
        {
            "path": "validator",
            "message": "custom validation failed",
            "expected": "callable",
            "got": "failed",
        },
        {
            "path": "db.password",
            "message": "missing required key",
            "expected": "required",
            "got": "missing",
        },
    ])

    assert err.issues[0]["expected"] == "callable"
    assert err.issues[0]["got"] == "failed"
    assert err.issues[1]["expected"] == "required"
    assert err.issues[1]["got"] == "missing"


def test_validationerror_copy_and_deepcopy_roundtrip_preserves_issues():
    err = ValidationError([
        {
            "path": "db.port",
            "message": "expected int, got str",
            "expected": "int",
            "got": "str",
        }
    ])

    for clone in (copy.copy(err), copy.deepcopy(err)):
        assert isinstance(clone, ValidationError)
        assert clone is not err
        assert clone.issues == err.issues
        assert clone.issues is not err.issues
        assert clone.issues[0] is not err.issues[0]
        assert str(clone) == str(err)


def test_validationerror_pickle_roundtrip_preserves_issues():
    err = ValidationError([
        {
            "path": "db.port",
            "message": "expected int, got str",
            "expected": "int",
            "got": "str",
        },
        {
            "path": "db.host",
            "message": "missing required key",
            "expected": "required",
            "got": "missing",
        },
    ])

    restored = pickle.loads(pickle.dumps(err))

    assert isinstance(restored, ValidationError)
    assert restored is not err
    assert restored.issues == err.issues
    assert restored.issues is not err.issues
    assert str(restored) == str(err)


# ── validate() error_mode tests ──────────────────────────────────────


def test_validate_structured_text_mode_raises_valueerror():
    """error_mode='text' raises ValueError, not ValidationError."""
    with pytest.raises(ValueError, match="expected int, got str") as exc_info:
        validate({"port": int}, {"port": "abc"}, error_mode="text")
    assert not isinstance(exc_info.value, ValidationError)


def test_validate_structured_text_mode_format_matches_existing():
    """error_mode='text' string matches legacy format exactly."""
    with pytest.raises(ValueError) as exc_info:
        validate({"port": int, "host": int}, {"port": "x", "host": "y"},
                 error_mode="text")
    assert str(exc_info.value) == "port: expected int, got str\nhost: expected int, got str"


def test_validate_structured_default_mode_raises_valueerror():
    """Omitting error_mode raises ValueError (backward compat)."""
    with pytest.raises(ValueError) as exc_info:
        validate({"port": int}, {"port": "abc"})
    assert not isinstance(exc_info.value, ValidationError)


def test_validate_structured_mode_raises_validation_error():
    """error_mode='structured' raises ValidationError."""
    with pytest.raises(ValidationError):
        validate({"port": int}, {"port": "abc"}, error_mode="structured")


def test_validate_structured_issues_correct_dict_per_error():
    """Each issue has exactly {path, message, expected, got}."""
    with pytest.raises(ValidationError) as exc_info:
        validate({"port": int}, {"port": "abc"}, error_mode="structured")
    issues = exc_info.value.issues
    assert len(issues) == 1
    assert set(issues[0].keys()) == {"path", "message", "expected", "got"}


def test_validate_structured_type_mismatch():
    """Type mismatch produces correct issue dict."""
    with pytest.raises(ValidationError) as exc_info:
        validate({"port": int}, {"port": "abc"}, error_mode="structured")
    issue = exc_info.value.issues[0]
    assert issue == {
        "path": "port",
        "message": "expected int, got str",
        "expected": "int",
        "got": "str",
    }


def test_validate_structured_missing_required_key():
    """Missing required key produces correct issue dict."""
    with pytest.raises(ValidationError) as exc_info:
        validate({"host": str}, {}, error_mode="structured")
    issue = exc_info.value.issues[0]
    assert issue == {
        "path": "host",
        "message": "missing required key",
        "expected": "required",
        "got": "missing",
    }


def test_validate_structured_coercion_failure():
    """Coercion failure produces correct issue dict."""
    with pytest.raises(ValidationError) as exc_info:
        validate({"port": int}, {"port": "abc"}, coerce=True,
                 error_mode="structured")
    issue = exc_info.value.issues[0]
    assert issue == {
        "path": "port",
        "message": "cannot coerce 'abc' to int",
        "expected": "int",
        "got": "str",
    }


def test_validate_structured_empty_string_coercion_failure():
    """Empty string coercion failure produces correct issue dict."""
    with pytest.raises(ValidationError) as exc_info:
        validate({"port": int}, {"port": ""}, coerce=True,
                 error_mode="structured")
    issue = exc_info.value.issues[0]
    assert issue == {
        "path": "port",
        "message": "cannot coerce empty string to int",
        "expected": "int",
        "got": "str",
    }


def test_validate_structured_custom_validator_returns_false():
    """Custom validator returning False produces correct issue dict."""
    with pytest.raises(ValidationError) as exc_info:
        validate({"email": lambda v: False}, {"email": "x"},
                 error_mode="structured")
    issue = exc_info.value.issues[0]
    assert issue == {
        "path": "email",
        "message": "custom validation failed",
        "expected": "callable",
        "got": "failed",
    }


def test_validate_structured_custom_validator_raises_exception():
    """Custom validator raising produces issue with exception info."""
    def bad_validator(v):
        raise ValueError("bad format")

    with pytest.raises(ValidationError) as exc_info:
        validate({"email": bad_validator}, {"email": "x"},
                 error_mode="structured")
    issue = exc_info.value.issues[0]
    assert issue == {
        "path": "email",
        "message": "custom validation failed (ValueError: bad format)",
        "expected": "callable",
        "got": "failed",
    }


def test_validate_structured_depth_exceeded():
    """Depth exceeded produces correct issue dict."""
    with pytest.raises(ValidationError) as exc_info:
        validate({"a": {"b": str}}, {"a": {"b": "x"}}, max_depth=1,
                 error_mode="structured")
    issue = exc_info.value.issues[0]
    assert issue == {
        "path": "a",
        "message": "max depth exceeded",
        "expected": "max_depth",
        "got": "exceeded",
    }


def test_validate_structured_unknown_key():
    """Unknown key produces correct issue dict."""
    with pytest.raises(ValidationError) as exc_info:
        validate({"name": str}, {"name": "a", "extra": 1},
                 error_mode="structured")
    issue = exc_info.value.issues[0]
    assert issue == {
        "path": "extra",
        "message": "unknown key",
        "expected": "known",
        "got": "unknown",
    }


def test_validate_structured_union_mismatch():
    """Union mismatch produces correct issue dict."""
    with pytest.raises(ValidationError) as exc_info:
        validate({"val": str | int}, {"val": True},
                 error_mode="structured")
    issue = exc_info.value.issues[0]
    assert issue == {
        "path": "val",
        "message": "expected str | int, got bool",
        "expected": "str | int",
        "got": "bool",
    }


def test_validate_structured_multiple_errors_all_collected():
    """Multiple errors are all collected in .issues."""
    with pytest.raises(ValidationError) as exc_info:
        validate({"a": int, "b": str, "c": float},
                 {"a": "x", "b": 1, "c": "y"},
                 error_mode="structured")
    assert len(exc_info.value.issues) == 3


def test_validate_structured_preserves_error_order():
    """Issues preserve internal error collection order (no re-sorting)."""
    with pytest.raises(ValidationError) as exc_info:
        validate({"a": int, "b": str, "c": float},
                 {"a": "x", "b": 1, "c": "y"},
                 error_mode="structured")
    paths = [i["path"] for i in exc_info.value.issues]
    assert paths == ["a", "b", "c"]


def test_validate_structured_valid_data_returns_dict():
    """Happy path: valid data returns dict, error_mode has no effect."""
    result = validate({"name": str, "age": int},
                      {"name": "Alice", "age": 30},
                      error_mode="structured")
    assert result == {"name": "Alice", "age": 30}


def test_validate_structured_caught_by_except_valueerror():
    """ValidationError is caught by except ValueError."""
    with pytest.raises(ValueError):
        validate({"port": int}, {"port": "abc"}, error_mode="structured")


def test_validate_structured_invalid_error_mode():
    """Invalid error_mode raises ValueError."""
    with pytest.raises(ValueError, match="error_mode must be 'text' or 'structured'"):
        validate({"a": int}, {"a": 1}, error_mode="invalid")


def test_validate_structured_multi_param_coerce_strip_depth():
    """Integration: structured + coerce + strip + max_depth."""
    with pytest.raises(ValidationError) as exc_info:
        validate(
            {"a": {"b": int}},
            {"a": {"b": "abc"}, "extra": 1},
            coerce=True,
            unknown_keys="strip",
            max_depth=2,
            error_mode="structured",
        )
    issues = exc_info.value.issues
    # Should have coercion failure for a.b, no unknown-key issue (stripped)
    assert len(issues) == 1
    assert issues[0]["path"] == "a.b"
    assert "coerce" in issues[0]["message"]


def test_validate_structured_multi_param_reject_unknown():
    """Integration: structured + reject unknown keys."""
    with pytest.raises(ValidationError) as exc_info:
        validate(
            {"name": str},
            {"name": "Alice", "extra": 1},
            unknown_keys="reject",
            error_mode="structured",
        )
    issues = exc_info.value.issues
    assert len(issues) == 1
    assert issues[0] == {
        "path": "extra",
        "message": "unknown key",
        "expected": "known",
        "got": "unknown",
    }


# ── Structured mode: composition coverage ────────────────────────────


def test_validate_structured_list_type_mismatch():
    """List-type mismatch produces correct issue dict in structured mode."""
    with pytest.raises(ValidationError) as exc_info:
        validate({"tags": [str]}, {"tags": "notalist"},
                 error_mode="structured")
    issue = exc_info.value.issues[0]
    assert issue == {
        "path": "tags",
        "message": "expected list, got str",
        "expected": "list",
        "got": "str",
    }


def test_validate_structured_dict_type_mismatch():
    """Dict-type mismatch produces correct issue dict in structured mode."""
    with pytest.raises(ValidationError) as exc_info:
        validate({"db": {"host": str}}, {"db": "notadict"},
                 error_mode="structured")
    issue = exc_info.value.issues[0]
    assert issue == {
        "path": "db",
        "message": "expected dict, got str",
        "expected": "dict",
        "got": "str",
    }


def test_validate_structured_nested_dot_path():
    """Deeply nested errors use dot-path formatting in .issues."""
    with pytest.raises(ValidationError) as exc_info:
        validate({"a": {"b": {"c": int}}}, {"a": {"b": {"c": "bad"}}},
                 error_mode="structured")
    issue = exc_info.value.issues[0]
    assert issue["path"] == "a.b.c"
    assert issue["expected"] == "int"
    assert issue["got"] == "str"


def test_validate_structured_optional_type_mismatch():
    """Optional key with type mismatch produces correct issue in structured mode."""
    from zodify import Optional
    with pytest.raises(ValidationError) as exc_info:
        validate({"port": Optional(int)}, {"port": "abc"},
                 error_mode="structured")
    issue = exc_info.value.issues[0]
    assert issue == {
        "path": "port",
        "message": "expected int, got str",
        "expected": "int",
        "got": "str",
    }


def test_validate_structured_list_element_error():
    """List element errors use bracket-index paths in structured mode."""
    with pytest.raises(ValidationError) as exc_info:
        validate({"tags": [str]}, {"tags": ["ok", 42]},
                 error_mode="structured")
    issue = exc_info.value.issues[0]
    assert issue == {
        "path": "tags[1]",
        "message": "expected str, got int",
        "expected": "str",
        "got": "int",
    }
