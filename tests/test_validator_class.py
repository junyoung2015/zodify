"""Tests for Validator defaults, overrides, and parity with bare validate()."""

import pytest

import zodify
from zodify import ValidationError, Validator, validate


def test_validator_exported_in_dunder_all() -> None:
    assert "Validator" in zodify.__all__


def test_validator_omitted_kwarg_uses_default_coerce() -> None:
    schema = {"port": int}
    data = {"port": "8080"}

    validator = Validator(coerce=True)

    assert validator.validate(schema, data) == {"port": 8080}


def test_validator_omitted_kwarg_uses_default_max_depth() -> None:
    schema = {"db": {"port": int}}
    data = {"db": {"port": 5432}}

    validator = Validator(max_depth=1)

    with pytest.raises(ValueError, match="db: max depth exceeded"):
        validator.validate(schema, data)


def test_validator_omitted_kwarg_uses_default_unknown_keys() -> None:
    schema = {"name": str}
    data = {"name": "kai", "age": 25}

    validator = Validator(unknown_keys="strip")

    assert validator.validate(schema, data) == {"name": "kai"}


def test_validator_omitted_kwarg_uses_default_error_mode() -> None:
    schema = {"port": int}
    data = {"port": "abc"}

    validator = Validator(coerce=True, error_mode="structured")

    with pytest.raises(ValidationError) as exc:
        validator.validate(schema, data)
    assert exc.value.issues == [
        {
            "path": "port",
            "message": "cannot coerce 'abc' to int",
            "expected": "int",
            "got": "str",
        }
    ]


def test_validator_combined_constructor_defaults_have_independent_effects() -> None:
    validator = Validator(
        coerce=True,
        max_depth=2,
        unknown_keys="strip",
        error_mode="structured",
    )

    assert validator.validate(
        {"port": int},
        {"port": "8080", "extra": "drop-me"},
    ) == {"port": 8080}

    with pytest.raises(ValidationError) as coerce_exc:
        validator.validate({"port": int}, {"port": "bad"})
    assert coerce_exc.value.issues == [
        {
            "path": "port",
            "message": "cannot coerce 'bad' to int",
            "expected": "int",
            "got": "str",
        }
    ]

    with pytest.raises(ValidationError) as depth_exc:
        validator.validate(
            {"db": {"inner": {"port": int}}},
            {"db": {"inner": {"port": "8080"}}},
        )
    assert depth_exc.value.issues == [
        {
            "path": "db.inner",
            "message": "max depth exceeded",
            "expected": "max_depth",
            "got": "exceeded",
        }
    ]

    assert validator.validate(
        {"db": {"port": int}},
        {"db": {"port": "8080"}},
    ) == {"db": {"port": 8080}}

    with pytest.raises(ValueError, match="extra: unknown key"):
        validator.validate(
            {"port": int},
            {"port": "8080", "extra": "kept"},
            unknown_keys="reject",
            error_mode="text",
        )


def test_default_validator_matches_bare_validate_for_pass_and_fail() -> None:
    schema = {"port": int}

    assert Validator().validate(schema, {"port": 8080}) == validate(schema, {"port": 8080})

    with pytest.raises(ValueError) as direct_exc:
        validate(schema, {"port": "8080"})
    with pytest.raises(ValueError) as wrapper_exc:
        Validator().validate(schema, {"port": "8080"})

    assert str(wrapper_exc.value) == str(direct_exc.value)


def test_validator_per_call_override_coerce_does_not_mutate_default() -> None:
    schema = {"port": int}
    data = {"port": "8080"}

    validator = Validator(coerce=False)

    assert validator.validate(schema, data, coerce=True) == {"port": 8080}
    with pytest.raises(ValueError, match="port: expected int, got str"):
        validator.validate(schema, data)


def test_validator_per_call_override_max_depth_does_not_mutate_default() -> None:
    schema = {"db": {"port": int}}
    data = {"db": {"port": 5432}}

    validator = Validator(max_depth=1)

    assert validator.validate(schema, data, max_depth=2) == {"db": {"port": 5432}}
    with pytest.raises(ValueError, match="db: max depth exceeded"):
        validator.validate(schema, data)


def test_validator_per_call_override_unknown_keys_does_not_mutate_default() -> None:
    schema = {"name": str}
    data = {"name": "kai", "age": 25}

    validator = Validator(unknown_keys="reject")

    assert validator.validate(schema, data, unknown_keys="strip") == {"name": "kai"}
    with pytest.raises(ValueError, match="age: unknown key"):
        validator.validate(schema, data)


def test_validator_per_call_override_error_mode_does_not_mutate_default() -> None:
    schema = {"port": int}
    data = {"port": "abc"}

    validator = Validator(coerce=True, error_mode="text")

    with pytest.raises(ValidationError):
        validator.validate(schema, data, error_mode="structured")

    with pytest.raises(ValueError, match="port: cannot coerce 'abc' to int"):
        validator.validate(schema, data)


def test_multiple_validators_are_isolated_interleaved_pattern_one() -> None:
    schema = {"name": str}
    data = {"name": "kai", "age": 25}

    validator_a = Validator(unknown_keys="strip")
    validator_b = Validator(unknown_keys="reject")

    with pytest.raises(ValueError, match="age: unknown key"):
        validator_a.validate(schema, data, unknown_keys="reject")
    with pytest.raises(ValueError, match="age: unknown key"):
        validator_b.validate(schema, data)
    assert validator_a.validate(schema, data) == {"name": "kai"}


def test_multiple_validators_are_isolated_interleaved_pattern_two() -> None:
    schema = {"port": int}
    data = {"port": "8080"}

    validator_a = Validator(coerce=True)
    validator_b = Validator(coerce=False)

    assert validator_b.validate(schema, data, coerce=True) == {"port": 8080}
    assert validator_a.validate(schema, data) == {"port": 8080}
    with pytest.raises(ValueError, match="port: expected int, got str"):
        validator_b.validate(schema, data)


def test_validator_text_failure_parity_unknown_keys_reject_single_error() -> None:
    schema = {"name": str}
    data = {"name": "kai", "age": 25}

    with pytest.raises(ValueError) as direct_exc:
        validate(schema, data, unknown_keys="reject")
    with pytest.raises(ValueError) as wrapper_exc:
        Validator(unknown_keys="reject").validate(schema, data)

    assert str(wrapper_exc.value) == str(direct_exc.value)


def test_validator_success_parity_unknown_keys_strip() -> None:
    schema = {"name": str}
    data = {"name": "kai", "age": 25}

    assert Validator(unknown_keys="strip").validate(schema, data) == validate(
        schema,
        data,
        unknown_keys="strip",
    )


def test_validator_text_failure_parity_type_mismatch_single_error() -> None:
    schema = {"port": int}
    data = {"port": "abc"}

    with pytest.raises(ValueError) as direct_exc:
        validate(schema, data)
    with pytest.raises(ValueError) as wrapper_exc:
        Validator().validate(schema, data)

    assert str(wrapper_exc.value) == str(direct_exc.value)


def test_validator_structured_failure_parity_single_error() -> None:
    schema = {"port": int}
    data = {"port": "abc"}

    with pytest.raises(ValidationError) as direct_exc:
        validate(schema, data, error_mode="structured")
    with pytest.raises(ValidationError) as wrapper_exc:
        Validator(error_mode="structured").validate(schema, data)

    assert wrapper_exc.value.issues == direct_exc.value.issues


def test_validator_constructor_invalid_unknown_keys_matches_bare_validate_contract() -> None:
    with pytest.raises(ValueError) as direct_exc:
        validate({"a": int}, {"a": 1}, unknown_keys="allow")  # type: ignore[arg-type]
    with pytest.raises(ValueError) as wrapper_exc:
        Validator(unknown_keys="allow")  # type: ignore[arg-type]

    assert str(wrapper_exc.value) == str(direct_exc.value)


def test_validator_constructor_invalid_error_mode_matches_bare_validate_contract() -> None:
    with pytest.raises(ValueError) as direct_exc:
        validate({"a": int}, {"a": 1}, error_mode="json")  # type: ignore[arg-type]
    with pytest.raises(ValueError) as wrapper_exc:
        Validator(error_mode="json")  # type: ignore[arg-type]

    assert str(wrapper_exc.value) == str(direct_exc.value)


def test_validator_override_invalid_unknown_keys_matches_bare_validate_contract() -> None:
    validator = Validator()

    with pytest.raises(ValueError) as direct_exc:
        validate({"a": int}, {"a": 1}, unknown_keys="allow")  # type: ignore[arg-type]
    with pytest.raises(ValueError) as wrapper_exc:
        validator.validate({"a": int}, {"a": 1}, unknown_keys="allow")  # type: ignore[arg-type]

    assert str(wrapper_exc.value) == str(direct_exc.value)


def test_validator_override_invalid_error_mode_matches_bare_validate_contract() -> None:
    validator = Validator()

    with pytest.raises(ValueError) as direct_exc:
        validate({"a": int}, {"a": 1}, error_mode="json")  # type: ignore[arg-type]
    with pytest.raises(ValueError) as wrapper_exc:
        validator.validate({"a": int}, {"a": 1}, error_mode="json")  # type: ignore[arg-type]

    assert str(wrapper_exc.value) == str(direct_exc.value)


def test_validator_schema_type_error_parity() -> None:
    validator = Validator()

    with pytest.raises(TypeError) as direct_exc:
        validate(["bad"], {})  # type: ignore[arg-type]
    with pytest.raises(TypeError) as wrapper_exc:
        validator.validate(["bad"], {})  # type: ignore[arg-type]

    assert str(wrapper_exc.value) == str(direct_exc.value)


def test_validator_data_type_error_parity() -> None:
    validator = Validator()

    with pytest.raises(TypeError) as direct_exc:
        validate({"a": int}, ["bad"])  # type: ignore[arg-type]
    with pytest.raises(TypeError) as wrapper_exc:
        validator.validate({"a": int}, ["bad"])  # type: ignore[arg-type]

    assert str(wrapper_exc.value) == str(direct_exc.value)


def test_validator_max_depth_type_error_parity_constructor_default() -> None:
    schema = {"db": {"port": int}}
    data = {"db": {"port": 5432}}

    with pytest.raises(TypeError) as direct_exc:
        validate(schema, data, max_depth="x")  # type: ignore[arg-type]
    with pytest.raises(TypeError) as wrapper_exc:
        Validator(max_depth="x").validate(schema, data)  # type: ignore[arg-type]

    assert str(wrapper_exc.value) == str(direct_exc.value)


def test_validator_max_depth_type_error_parity_call_override() -> None:
    schema = {"db": {"port": int}}
    data = {"db": {"port": 5432}}
    validator = Validator(max_depth=2)

    with pytest.raises(TypeError) as direct_exc:
        validate(schema, data, max_depth="x")  # type: ignore[arg-type]
    with pytest.raises(TypeError) as wrapper_exc:
        validator.validate(schema, data, max_depth="x")  # type: ignore[arg-type]

    assert str(wrapper_exc.value) == str(direct_exc.value)


def test_validator_preserves_non_bool_coerce_parity_constructor_default() -> None:
    schema = {"count": int}
    data = {"count": "1"}

    direct = validate(schema, data, coerce="yes")  # type: ignore[arg-type]
    wrapped = Validator(coerce="yes").validate(schema, data)  # type: ignore[arg-type]

    assert wrapped == direct == {"count": 1}


def test_validator_preserves_non_bool_coerce_parity_call_override() -> None:
    schema = {"count": int}
    data = {"count": "2"}
    validator = Validator(coerce=False)

    direct = validate(schema, data, coerce="yes")  # type: ignore[arg-type]
    wrapped = validator.validate(schema, data, coerce="yes")  # type: ignore[arg-type]

    assert wrapped == direct == {"count": 2}


def test_validator_validate_delegates_to_validate_api_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_validate(schema, data, *, coerce, max_depth, unknown_keys, error_mode):
        captured["schema"] = schema
        captured["data"] = data
        captured["coerce"] = coerce
        captured["max_depth"] = max_depth
        captured["unknown_keys"] = unknown_keys
        captured["error_mode"] = error_mode
        return {"ok": True}

    monkeypatch.setattr(zodify, "validate", fake_validate)

    validator = Validator(coerce=True, max_depth=3, unknown_keys="strip", error_mode="structured")
    result = validator.validate({"a": int}, {"a": "1"})

    assert result == {"ok": True}
    assert captured == {
        "schema": {"a": int},
        "data": {"a": "1"},
        "coerce": True,
        "max_depth": 3,
        "unknown_keys": "strip",
        "error_mode": "structured",
    }
