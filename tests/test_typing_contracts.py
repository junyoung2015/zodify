"""Typing contract tests"""

from typing import Any, Literal, get_origin, get_type_hints

import pytest
import zodify


def test_module_level_annotations_exist():
    assert zodify.__annotations__["__version__"] is str
    assert zodify.__annotations__["_MISSING"] is object


def test_optional_class_attributes_and_methods_are_annotated():
    class_hints = get_type_hints(zodify.Optional)
    assert class_hints["type"] is Any
    assert class_hints["default"] is Any

    init_hints = get_type_hints(zodify.Optional.__init__)
    assert init_hints["type"] is Any
    assert init_hints["default"] is Any
    assert init_hints["return"] is type(None)

    repr_hints = get_type_hints(zodify.Optional.__repr__)
    assert repr_hints["return"] is str


def test_validate_signature_has_literal_unknown_keys_mode():
    hints = get_type_hints(zodify.validate)
    assert hints["schema"] == dict[str, Any]
    assert hints["data"] == dict[str, Any]
    assert hints["coerce"] is bool
    assert hints["max_depth"] is int
    assert hints["unknown_keys"] == Literal["reject", "strip"]
    assert hints["return"] == dict[str, Any]


def test_internal_functions_use_literal_unknown_keys_mode():
    check_hints = get_type_hints(zodify._check_value)
    validate_hints = get_type_hints(zodify._validate)
    assert check_hints["unknown_keys"] == Literal["reject", "strip"]
    assert validate_hints["unknown_keys"] == Literal["reject", "strip"]


def test_env_signature_is_generic_over_cast_type():
    hints = get_type_hints(zodify.env)
    cast_annotation = hints["cast"]
    assert get_origin(cast_annotation) is type

    return_annotation = hints["return"]
    assert type(return_annotation).__name__ == "TypeVar"
    assert hints["default"] is object


def test_validate_rejects_invalid_unknown_keys_runtime_mode():
    with pytest.raises(ValueError):
        zodify.validate({"a": int}, {"a": 1}, unknown_keys="bad")  # type: ignore[arg-type]
