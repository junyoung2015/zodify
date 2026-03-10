"""Typing contract tests"""

from pathlib import Path
from typing import Any, Literal, get_origin, get_type_hints

import pytest
import zodify

SCHEMA_TYPING_CONTRACT = (
    Path(__file__).resolve().parent / "typing" / "test_schema_class_typing_contract.py"
)
SCHEMA_RUNTIME_SMOKE = Path(__file__).resolve().parent / "test_schema_class.py"


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
    assert hints["data"] == dict[str, Any]
    assert hints["coerce"] is bool
    assert hints["max_depth"] is int
    assert hints["unknown_keys"] == Literal["reject", "strip"]
    if not hasattr(zodify, "Schema"):
        assert hints["schema"] == dict[str, Any]
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


def test_schema_typing_contract_switches_to_live_api_once_schema_is_public():
    if not hasattr(zodify, "Schema"):
        return

    contract_text = SCHEMA_TYPING_CONTRACT.read_text(encoding="utf-8")
    assert "from zodify import Schema, Validator, validate" in contract_text
    assert "from tests.typing import" not in contract_text


def test_live_schema_smoke_file_exists():
    assert SCHEMA_RUNTIME_SMOKE.exists()
