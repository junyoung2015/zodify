"""Prototype module for class-based schema validation research.

Non-production code used for feasibility validation without changing
the live zodify runtime.
"""

from __future__ import annotations

import types
from typing import Any, ClassVar, Literal, TypeVar, cast, get_args, get_origin, overload

import zodify

_SchemaT = TypeVar("_SchemaT", bound="Schema")
UnknownKeysMode = Literal["reject", "strip"]
ErrorMode = Literal["text", "structured"]
_DICT_METHOD_NAMES = frozenset(dir(dict))


class ValidatedDict(dict[str, Any]):
    """Prototype dict subtype with attribute access for schema fields."""

    __slots__ = ()
    __schema_fields__: frozenset[str] = frozenset()
    __blocked_fields__: frozenset[str] = frozenset()

    def __getattr__(self, name: str) -> Any:
        if name in self:
            return self[name]
        raise AttributeError(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            super().__setattr__(name, value)
            return
        if name in type(self).__blocked_fields__:
            raise AttributeError(
                f"{name}: attribute access is blocked by an existing dict method;"
                " use key access instead"
            )
        if name in type(self).__schema_fields__:
            self[name] = value
            return
        raise AttributeError(name)

    def __delattr__(self, name: str) -> None:
        if name in type(self).__blocked_fields__:
            raise AttributeError(
                f"{name}: attribute access is blocked by an existing dict method;"
                " use key deletion instead"
            )
        if name in type(self).__schema_fields__:
            try:
                del self[name]
            except KeyError as exc:
                raise AttributeError(name) from exc
            return
        raise AttributeError(name)


class Schema:
    """Prototype base class that compiles annotations into a dict schema."""

    __zodify_schema__: dict[str, Any] = {}
    __schema_fields__: frozenset[str] = frozenset()
    __blocked_fields__: frozenset[str] = frozenset()
    __nested_schema_fields__: dict[str, type["Schema"]] = {}
    __list_nested_schema_fields__: dict[str, type["Schema"]] = {}
    __validated_dict_type__: type[ValidatedDict] = ValidatedDict

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        if cls.__dict__.get("__schema_result_type__", False):
            return

        raw_annotations = dict(cls.__dict__.get("__annotations__", {}))
        compiled_schema: dict[str, Any] = {}
        nested_schema_fields: dict[str, type[Schema]] = {}
        list_nested_schema_fields: dict[str, type[Schema]] = {}
        schema_fields: list[str] = []

        for field_name, annotation in raw_annotations.items():
            if _is_classvar(annotation):
                continue
            if isinstance(annotation, str):
                raise TypeError(
                    f"{cls.__name__}.{field_name}: forward references are unsupported"
                )
            default = cls.__dict__.get(field_name, _MISSING)
            if _looks_like_deferred_callable_field(default):
                raise TypeError(
                    f"{cls.__name__}.{field_name}: callable field validators are deferred"
                )

            schema_value, nested_schema, list_nested_schema = _compile_annotation(
                cls,
                field_name,
                annotation,
            )
            if default is not _MISSING:
                schema_value = zodify.Optional(schema_value, default)

            compiled_schema[field_name] = schema_value
            schema_fields.append(field_name)
            if nested_schema is not None:
                nested_schema_fields[field_name] = nested_schema
            if list_nested_schema is not None:
                list_nested_schema_fields[field_name] = list_nested_schema

        cls.__zodify_schema__ = compiled_schema
        cls.__schema_fields__ = frozenset(schema_fields)
        cls.__blocked_fields__ = frozenset(
            name for name in schema_fields if name in _DICT_METHOD_NAMES
        )
        cls.__nested_schema_fields__ = nested_schema_fields
        cls.__list_nested_schema_fields__ = list_nested_schema_fields
        cls.__validated_dict_type__ = cast(
            type[ValidatedDict],
            type(
                f"{cls.__name__}ValidatedDict",
                (ValidatedDict, cls),
                {
                    "__module__": cls.__module__,
                    "__schema_result_type__": True,
                    "__schema_fields__": cls.__schema_fields__,
                    "__blocked_fields__": cls.__blocked_fields__,
                },
            ),
        )


_MISSING = object()


def _is_classvar(annotation: Any) -> bool:
    return get_origin(annotation) is ClassVar


def _looks_like_deferred_callable_field(default: Any) -> bool:
    return isinstance(default, (staticmethod, classmethod)) or callable(default)


def _compile_annotation(
    owner: type[Schema],
    field_name: str,
    annotation: Any,
) -> tuple[Any, type[Schema] | None, type[Schema] | None]:
    if isinstance(annotation, type) and issubclass(annotation, Schema):
        return annotation.__zodify_schema__, annotation, None

    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is list:
        if len(args) != 1:
            raise TypeError(
                f"{owner.__name__}.{field_name}: list annotations must contain exactly one item type"
            )
        item_schema, nested_schema, _ = _compile_annotation(owner, field_name, args[0])
        return [item_schema], None, nested_schema

    if origin is dict:
        return dict, None, None

    if origin is types.UnionType:
        return annotation, None, None

    if isinstance(annotation, type):
        return annotation, None, None

    raise TypeError(
        f"{owner.__name__}.{field_name}: unsupported schema annotation {annotation!r}"
    )


def _wrap_schema_result(schema: type[_SchemaT], payload: dict[str, Any]) -> _SchemaT:
    wrapped: dict[str, Any] = {}
    for key, value in payload.items():
        if key in schema.__nested_schema_fields__ and isinstance(value, dict):
            nested_schema = schema.__nested_schema_fields__[key]
            wrapped[key] = _wrap_schema_result(nested_schema, value)
            continue
        if key in schema.__list_nested_schema_fields__ and isinstance(value, list):
            nested_schema = schema.__list_nested_schema_fields__[key]
            wrapped[key] = [
                _wrap_schema_result(nested_schema, item)
                if isinstance(item, dict)
                else item
                for item in value
            ]
            continue
        wrapped[key] = value
    return cast(_SchemaT, schema.__validated_dict_type__(wrapped))


@overload
def validate(
    schema: type[_SchemaT],
    data: dict[str, Any],
    *,
    coerce: bool = False,
    max_depth: int = 32,
    unknown_keys: UnknownKeysMode = "reject",
    error_mode: ErrorMode = "text",
) -> _SchemaT:
    ...


@overload
def validate(
    schema: dict[str, Any],
    data: dict[str, Any],
    *,
    coerce: bool = False,
    max_depth: int = 32,
    unknown_keys: UnknownKeysMode = "reject",
    error_mode: ErrorMode = "text",
) -> dict[str, Any]:
    ...


def validate(
    schema: type[_SchemaT] | dict[str, Any],
    data: dict[str, Any],
    *,
    coerce: bool = False,
    max_depth: int = 32,
    unknown_keys: UnknownKeysMode = "reject",
    error_mode: ErrorMode = "text",
) -> _SchemaT | dict[str, Any]:
    if type(schema) is dict:
        return zodify.validate(
            schema,
            data,
            coerce=coerce,
            max_depth=max_depth,
            unknown_keys=unknown_keys,
            error_mode=error_mode,
        )
    if isinstance(schema, type) and issubclass(schema, Schema):
        normalized_schema = schema.__zodify_schema__
        validated = zodify.validate(
            normalized_schema,
            data,
            coerce=coerce,
            max_depth=max_depth,
            unknown_keys=unknown_keys,
            error_mode=error_mode,
        )
        return _wrap_schema_result(schema, validated)
    raise TypeError("schema must be a dict or Schema subclass")


class Validator:
    """Prototype wrapper that accepts Schema subclasses."""

    __slots__ = ("_validator",)

    def __init__(
        self,
        *,
        coerce: bool = False,
        max_depth: int = 32,
        unknown_keys: UnknownKeysMode = "reject",
        error_mode: ErrorMode = "text",
    ) -> None:
        self._validator = zodify.Validator(
            coerce=coerce,
            max_depth=max_depth,
            unknown_keys=unknown_keys,
            error_mode=error_mode,
        )

    @overload
    def validate(
        self,
        schema: type[_SchemaT],
        data: dict[str, Any],
        *,
        coerce: bool = False,
        max_depth: int = 32,
        unknown_keys: UnknownKeysMode = "reject",
        error_mode: ErrorMode = "text",
    ) -> _SchemaT:
        ...

    @overload
    def validate(
        self,
        schema: dict[str, Any],
        data: dict[str, Any],
        *,
        coerce: bool = False,
        max_depth: int = 32,
        unknown_keys: UnknownKeysMode = "reject",
        error_mode: ErrorMode = "text",
    ) -> dict[str, Any]:
        ...

    def validate(
        self,
        schema: type[_SchemaT] | dict[str, Any],
        data: dict[str, Any],
        *,
        coerce: bool = False,
        max_depth: int = 32,
        unknown_keys: UnknownKeysMode = "reject",
        error_mode: ErrorMode = "text",
    ) -> _SchemaT | dict[str, Any]:
        if type(schema) is dict:
            return self._validator.validate(
                schema,
                data,
                coerce=coerce,
                max_depth=max_depth,
                unknown_keys=unknown_keys,
                error_mode=error_mode,
            )
        if isinstance(schema, type) and issubclass(schema, Schema):
            validated = self._validator.validate(
                schema.__zodify_schema__,
                data,
                coerce=coerce,
                max_depth=max_depth,
                unknown_keys=unknown_keys,
                error_mode=error_mode,
            )
            return _wrap_schema_result(schema, validated)
        raise TypeError("schema must be a dict or Schema subclass")
