"""Tests for custom validator functions."""

import pytest
import zodify
from zodify import validate, Optional


# --- Lambda passes ---

def test_validate_lambda_passes_port_in_range():
    result = validate({"port": lambda v: 1 <= v <= 65535}, {"port": 8080})
    assert result == {"port": 8080}


def test_validate_lambda_passes_returns_value():
    result = validate({"name": lambda v: isinstance(v, str) and len(v) > 0}, {"name": "alice"})
    assert result == {"name": "alice"}


# --- Lambda fails (returns False) ---

def test_validate_lambda_returns_false_error():
    with pytest.raises(ValueError, match="custom validation failed"):
        validate({"port": lambda v: 1 <= v <= 65535}, {"port": 99999})


# --- Named function raises ---

def _check_positive(v):
    if v <= 0:
        raise ValueError("must be positive")
    return True


def test_validate_named_function_raises_error():
    with pytest.raises(ValueError, match="custom validation failed"):
        validate({"count": _check_positive}, {"count": -1})


def test_validate_named_function_passes():
    result = validate({"count": _check_positive}, {"count": 5})
    assert result == {"count": 5}


# --- Type vs callable distinction ---

def test_validate_int_type_uses_type_path_not_callable():
    """int is callable but type(int) is type, so it must use the type path."""
    with pytest.raises(ValueError, match="expected int, got str"):
        validate({"a": int}, {"a": "x"})


def test_validate_str_type_uses_type_path_not_callable():
    with pytest.raises(ValueError, match="expected str, got int"):
        validate({"a": str}, {"a": 42})


# --- Dispatch precedence ---

def test_validate_callable_class_instance_accepted():
    """A callable object (not a type) should go through the callable path."""
    class RangeCheck:
        def __call__(self, v):
            return 0 <= v <= 100
    result = validate({"score": RangeCheck()}, {"score": 50})
    assert result == {"score": 50}


def test_validate_non_callable_schema_raises_typeerror():
    """Non-callable, non-type schema value must raise TypeError."""
    with pytest.raises(TypeError, match="invalid schema value"):
        validate({"a": 42}, {"a": 1})


# --- Validator contract ---

def test_validate_callable_receives_one_arg_exactly_once():
    """Validator receives exactly one argument (the value), called exactly once."""
    received = []
    def capture(v):
        received.append(v)
        return True
    validate({"x": capture}, {"x": "hello"})
    assert received == ["hello"]
    assert len(received) == 1


# --- None passthrough ---

def test_validate_none_passed_to_validator():
    """None is passed directly to the validator, not type-checked first."""
    with pytest.raises(ValueError, match="custom validation failed"):
        validate({"x": lambda v: v > 0}, {"x": None})


# --- Error tuple format ---

def test_validate_callable_error_tuple_format():
    """Error tuple: (path, 'custom validation failed', 'callable', 'failed')."""
    try:
        validate({"port": lambda v: 1 <= v <= 65535}, {"port": 99999})
        assert False, "should have raised"
    except ValueError as e:
        assert "port: custom validation failed" in str(e)


def test_validate_callable_truthy_non_true():
    """Truthy non-True values (1, 'yes') should pass."""
    result = validate({"x": lambda v: 1}, {"x": "anything"})
    assert result == {"x": "anything"}


def test_validate_callable_falsy_non_false():
    """Falsy non-False values (0, '', None) should fail."""
    with pytest.raises(ValueError, match="custom validation failed"):
        validate({"x": lambda v: 0}, {"x": "anything"})


# --- Optional(callable) ---

def test_validate_optional_callable_key_present_runs_validator():
    """When key is present, callable validator runs on the value."""
    result = validate(
        {"port": Optional(lambda v: 1 <= v <= 65535, default=5)},
        {"port": 8080},
    )
    assert result == {"port": 8080}


def test_validate_optional_callable_key_missing_applies_default():
    """When key is missing, default is applied without running validator."""
    result = validate(
        {"port": Optional(lambda v: 1 <= v <= 65535, default=5)},
        {},
    )
    assert result == {"port": 5}


def test_validate_optional_callable_no_default_key_absent():
    """Optional(callable) with no default — key absent omits from result."""
    result = validate(
        {"port": Optional(lambda v: 1 <= v <= 65535)},
        {},
    )
    assert result == {}


# --- Edge cases ---

def test_validate_callable_with_coerce_flag():
    """coerce flag is irrelevant for callable — callable handles everything."""
    result = validate(
        {"port": lambda v: 1 <= v <= 65535},
        {"port": 8080},
        coerce=True,
    )
    assert result == {"port": 8080}


def test_validate_callable_in_nested_dict_schema():
    """Callable inside a nested dict schema."""
    result = validate(
        {"db": {"port": lambda v: 1 <= v <= 65535}},
        {"db": {"port": 443}},
    )
    assert result == {"db": {"port": 443}}


def test_validate_callable_in_typed_list_schema():
    """Callable as the element type in a list schema [callable]."""
    result = validate(
        {"scores": [lambda v: v > 0]},
        {"scores": [10, 20, 30]},
    )
    assert result == {"scores": [10, 20, 30]}


def test_validate_callable_in_typed_list_schema_failure():
    """Callable in list schema — one element fails."""
    with pytest.raises(ValueError, match="custom validation failed"):
        validate(
            {"scores": [lambda v: v > 0]},
            {"scores": [10, -5, 30]},
        )


def test_validate_callable_with_unknown_keys_reject():
    """unknown_keys='reject' still rejects unknown keys independently of callable."""
    with pytest.raises(ValueError, match="unknown key"):
        validate(
            {"port": lambda v: 1 <= v <= 65535},
            {"port": 8080, "extra": "bad"},
            unknown_keys="reject",
        )


# --- Direct tuple assertion ---

def test_validate_callable_error_tuple_contract_fields():
    """Directly verify the 4-tuple fields (path, msg, 'callable', 'failed')."""
    errors = []
    zodify._check_value(99999, lambda v: 1 <= v <= 65535, "port",
                        False, errors, 32, "reject")
    assert len(errors) == 1
    path, msg, expected, got = errors[0]
    assert path == "port"
    assert msg.startswith("custom validation failed")
    assert expected == "callable"
    assert got == "failed"


def test_validate_callable_error_includes_exception_detail():
    """Raised validator exceptions should preserve useful detail."""
    def raises(v):
        raise RuntimeError(f"boom {v}")

    with pytest.raises(ValueError, match="RuntimeError: boom 3"):
        validate({"x": raises}, {"x": 3})


# --- P1 Fix: Wrong-arity callables ---

def test_validate_callable_zero_args_fails_gracefully():
    """Zero-arg lambda raises TypeError internally, caught as validation failure."""
    with pytest.raises(ValueError, match="custom validation failed"):
        validate({"x": lambda: True}, {"x": 42})


def test_validate_callable_two_args_fails_gracefully():
    """Two-arg lambda raises TypeError internally, caught as validation failure."""
    with pytest.raises(ValueError, match="custom validation failed"):
        validate({"x": lambda a, b: True}, {"x": 42})


# --- P1 Fix: Explicit None return ---

def test_validate_callable_returns_none_fails():
    """Validator returning None (falsy) should fail validation."""
    with pytest.raises(ValueError, match="custom validation failed"):
        validate({"x": lambda v: None}, {"x": "anything"})


# --- P1 Fix: User-defined class uses type path ---

def test_validate_user_defined_class_uses_type_path():
    """User-defined class (type(Foo) is type) must use type path, not callable."""
    class Foo:
        pass
    with pytest.raises(ValueError, match="expected Foo, got str"):
        validate({"x": Foo}, {"x": "not a Foo"})


# --- P2 Fix: Callable + max_depth interaction ---

def test_validate_callable_nested_with_max_depth_exceeded():
    """Depth exceeded before reaching callable in nested dict."""
    with pytest.raises(ValueError) as exc_info:
        validate(
            {"a": {"b": lambda v: v > 0}},
            {"a": {"b": 5}},
            max_depth=1,
        )
    msg = str(exc_info.value)
    assert "max depth exceeded" in msg
    assert "custom validation failed" not in msg


# --- P2 Fix: Multi-error collection in list ---

def test_validate_callable_in_list_collects_all_errors():
    """All failing elements in a list produce individual error tuples."""
    with pytest.raises(ValueError) as exc_info:
        validate(
            {"scores": [lambda v: v > 0]},
            {"scores": [-1, -2, -3]},
        )
    msg = str(exc_info.value)
    assert msg.count("custom validation failed") == 3
    assert "scores[0]" in msg
    assert "scores[1]" in msg
    assert "scores[2]" in msg
