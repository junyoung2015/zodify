"""Executable schema design reference.

This is not production code. It models the extracted runtime shape used by the
public API:

- `zodify/schema.py` owns Schema compilation, normalization, and wrapped results
- `zodify/__init__.py` stays the public entrypoint and delegates into the
  existing dict engine after normalization
"""

from __future__ import annotations

import keyword
import types
from typing import Any, ClassVar, Literal, TypeVar, Union, cast, get_args, get_origin, overload

import zodify

_SchemaT = TypeVar("_SchemaT", bound="Schema")
_DictValueT = TypeVar("_DictValueT")
_SchemaValueT = TypeVar("_SchemaValueT")
UnknownKeysMode = Literal["reject", "strip"]
ErrorMode = Literal["text", "structured"]
_DICT_METHOD_NAMES = frozenset(dir(dict))
_MISSING = object()


class ValidatedDict(dict[str, Any]):
    """Dict subtype used as the runtime carrier for Schema validation."""

    __slots__ = ()
    __schema_fields__: frozenset[str] = frozenset()
    __nested_schema_fields__: dict[str, type["Schema"]] = {}
    __list_nested_schema_fields__: dict[str, type["Schema"]] = {}

    def __getattribute__(self, name: str) -> Any:
        cls = type(self)
        if name in cls.__schema_fields__:
            if dict.__contains__(self, name):
                return dict.__getitem__(self, name)
            raise AttributeError(name)
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in type(self).__schema_fields__:
            self[name] = value; return
        if name.startswith("_"):
            super().__setattr__(name, value); return
        raise AttributeError(name)

    def __delattr__(self, name: str) -> None:
        if name in type(self).__schema_fields__:
            if name not in self: raise AttributeError(name)
            del self[name]; return
        if name.startswith("_"):
            super().__delattr__(name); return
        raise AttributeError(name)

    def __setitem__(self, key: str, value: Any) -> None:
        if key in type(self).__schema_fields__:
            value = _wrap_schema_field_value(type(self), key, value)
        super().__setitem__(key, value)

    def update(self, *args: Any, **kwargs: Any) -> None:
        for key, value in dict(*args, **kwargs).items(): self[key] = value

    def setdefault(self, key: str, default: Any = None) -> Any:
        if key in self:
            return self[key]
        self[key] = default
        return self[key]

    def __ior__(self, other: Any) -> "ValidatedDict":  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
        self.update(other); return self

    def __or__(self, other: Any) -> dict[str, Any]:  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
        if not isinstance(other, dict): return NotImplemented
        merged = type(self)(); merged.update(self); merged.update(other); return cast(dict[str, Any], merged)

    def __ror__(self, other: Any) -> dict[str, Any]:  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
        if not isinstance(other, dict): return NotImplemented
        merged = type(self)(); merged.update(other); merged.update(self); return cast(dict[str, Any], merged)


class Schema:
    """Compiles direct annotations into a plain dict schema at class definition."""

    __zodify_schema__: dict[str, Any] = {}
    __schema_fields__: frozenset[str] = frozenset()
    __nested_schema_fields__: dict[str, type["Schema"]] = {}
    __list_nested_schema_fields__: dict[str, type["Schema"]] = {}
    __validated_dict_type__: type[ValidatedDict] = ValidatedDict

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if type(self).__dict__.get("__schema_result_type__", False): return
        raise TypeError(
            f"{type(self).__name__}: Schema declarations cannot be instantiated directly; "
            f"use validate({type(self).__name__}, data)"
        )

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        if cls.__dict__.get("__schema_result_type__", False):
            return
        if cls.__bases__ != (Schema,):
            raise TypeError(
                f"{cls.__name__}: inheritance beyond direct Schema subclassing is unsupported"
            )

        raw_annotations = dict(cls.__dict__.get("__annotations__", {}))
        compiled_schema: dict[str, Any] = {}
        nested_schema_fields: dict[str, type[Schema]] = {}
        list_nested_schema_fields: dict[str, type[Schema]] = {}
        schema_fields: list[str] = []

        for field_name, annotation in raw_annotations.items():
            if field_name.startswith("__") and field_name.endswith("__"):
                continue
            if not field_name.isidentifier() or keyword.iskeyword(field_name):
                raise TypeError(
                    f"{cls.__name__}.{field_name}: invalid identifier field names are unsupported; "
                    "use plain dict schemas for those cases"
                )
            if field_name in _DICT_METHOD_NAMES:
                raise TypeError(
                    f"{cls.__name__}.{field_name}: dict method names are unsupported in Schema fields; "
                    "use plain dict schemas for those cases"
                )
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

            schema_value, nested_schema, list_nested_schema = _compile_annotation(cls, field_name, annotation)
            if default is not _MISSING:
                schema_value = zodify.Optional(schema_value, default)

            compiled_schema[field_name] = schema_value
            schema_fields.append(field_name)
            if nested_schema is not None: nested_schema_fields[field_name] = nested_schema
            if list_nested_schema is not None: list_nested_schema_fields[field_name] = list_nested_schema

        cls.__zodify_schema__ = compiled_schema
        cls.__schema_fields__ = frozenset(schema_fields)
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
                    "__nested_schema_fields__": cls.__nested_schema_fields__,
                    "__list_nested_schema_fields__": cls.__list_nested_schema_fields__,
                },
            ),
        )


def _is_classvar(annotation: Any) -> bool:
    return get_origin(annotation) is ClassVar


def _looks_like_deferred_callable_field(default: Any) -> bool:
    return isinstance(default, (staticmethod, classmethod)) or callable(default)


def _compile_annotation(
    owner: type[Schema],
    field_name: str,
    annotation: Any,
) -> tuple[Any, type[Schema] | None, type[Schema] | None]:
    if annotation is Schema:
        raise TypeError(
            f"{owner.__name__}.{field_name}: nested fields must use a concrete Schema subclass"
        )
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
        if args:
            raise TypeError(
                f"{owner.__name__}.{field_name}: parameterized dict annotations are unsupported; use bare dict or nested Schema"
            )
        return dict, None, None

    if origin is types.UnionType or origin is Union:
        return _compile_union_annotation(owner, field_name, args), None, None

    if isinstance(annotation, type):
        return annotation, None, None

    raise TypeError(
        f"{owner.__name__}.{field_name}: unsupported schema annotation {annotation!r}"
    )


def is_schema_type(schema: object) -> bool:
    return isinstance(schema, type) and issubclass(schema, Schema)


def _compile_union_annotation(owner: type[Schema], field_name: str, args: tuple[Any, ...]) -> Any:
    normalized: Any = args[0]
    if get_origin(normalized) is not None or not isinstance(normalized, type) or issubclass(normalized, Schema):
        raise TypeError(
            f"{owner.__name__}.{field_name}: unions containing Schema subclasses or parameterized containers are unsupported; "
            "use plain dict schemas for those cases"
        )
    for option in args[1:]:
        if get_origin(option) is not None or not isinstance(option, type) or issubclass(option, Schema):
            raise TypeError(
                f"{owner.__name__}.{field_name}: unions containing Schema subclasses or parameterized containers are unsupported; "
                "use plain dict schemas for those cases"
            )
        normalized = normalized | option
    return normalized


def normalize_schema_input(
    schema: type[_SchemaT] | dict[str, Any],
) -> tuple[dict[str, Any], type[_SchemaT] | None]:
    if not isinstance(schema, type):
        return schema, None
    if issubclass(schema, Schema):
        return schema.__zodify_schema__, schema
    raise TypeError("schema must be a dict or Schema subclass")


def wrap_schema_result(schema: type[_SchemaT], payload: dict[str, Any]) -> _SchemaT:
    wrapped: dict[str, Any] = {}
    for key, value in payload.items():
        wrapped[key] = _wrap_schema_field_value(schema, key, value)
    return cast(_SchemaT, schema.__validated_dict_type__(wrapped))


def _wrap_schema_field_value(schema: type[ValidatedDict] | type[Schema], key: str, value: Any) -> Any:
    nested_schema_fields = getattr(schema, "__nested_schema_fields__", {})
    if key in nested_schema_fields and isinstance(value, dict):
        return wrap_schema_result(nested_schema_fields[key], value)

    list_nested_schema_fields = getattr(schema, "__list_nested_schema_fields__", {})
    if key in list_nested_schema_fields and isinstance(value, list):
        nested_schema = list_nested_schema_fields[key]
        return [
            wrap_schema_result(nested_schema, item) if isinstance(item, dict) else item
            for item in value
        ]

    return value


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
    schema: dict[str, type[_SchemaValueT]],
    data: dict[str, Any],
    *,
    coerce: bool = False,
    max_depth: int = 32,
    unknown_keys: Literal["reject"] = "reject",
    error_mode: ErrorMode = "text",
) -> dict[str, _SchemaValueT]:
    ...


@overload
def validate(
    schema: dict[str, Any],
    data: dict[str, _DictValueT],
    *,
    coerce: bool = False,
    max_depth: int = 32,
    unknown_keys: Literal["reject"] = "reject",
    error_mode: ErrorMode = "text",
) -> dict[str, _DictValueT]:
    ...


@overload
def validate(
    schema: dict[str, Any],
    data: dict[str, Any],
    *,
    coerce: bool = False,
    max_depth: int = 32,
    unknown_keys: Literal["strip"],
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
    normalized_schema, schema_type = normalize_schema_input(schema)
    validated = zodify.validate(
        normalized_schema,
        data,
        coerce=coerce,
        max_depth=max_depth,
        unknown_keys=unknown_keys,
        error_mode=error_mode,
    )
    if schema_type is None:
        return validated
    return wrap_schema_result(schema_type, validated)


class Validator:
    """Sketch for the `Validator.validate(...)` integration path."""

    __slots__ = ("coerce", "max_depth", "unknown_keys", "error_mode")

    coerce: bool
    max_depth: int
    unknown_keys: UnknownKeysMode
    error_mode: ErrorMode

    def __init__(
        self,
        *,
        coerce: bool = False,
        max_depth: int = 32,
        unknown_keys: UnknownKeysMode = "reject",
        error_mode: ErrorMode = "text",
    ) -> None:
        self.coerce = coerce
        self.max_depth = max_depth
        self.unknown_keys = unknown_keys
        self.error_mode = error_mode

    @overload
    def validate(
        self,
        schema: type[_SchemaT],
        data: dict[str, Any],
        *,
        coerce: bool = ...,
        max_depth: int = ...,
        unknown_keys: UnknownKeysMode = ...,
        error_mode: ErrorMode = ...,
    ) -> _SchemaT:
        ...

    @overload
    def validate(
        self,
        schema: dict[str, type[_SchemaValueT]],
        data: dict[str, Any],
        *,
        coerce: bool = ...,
        max_depth: int = ...,
        unknown_keys: Literal["reject"] = ...,
        error_mode: ErrorMode = ...,
    ) -> dict[str, _SchemaValueT]:
        ...

    @overload
    def validate(
        self,
        schema: dict[str, Any],
        data: dict[str, _DictValueT],
        *,
        coerce: bool = ...,
        max_depth: int = ...,
        unknown_keys: Literal["reject"] = ...,
        error_mode: ErrorMode = ...,
    ) -> dict[str, _DictValueT]:
        ...

    @overload
    def validate(
        self,
        schema: dict[str, Any],
        data: dict[str, Any],
        *,
        coerce: bool = ...,
        max_depth: int = ...,
        unknown_keys: Literal["strip"],
        error_mode: ErrorMode = ...,
    ) -> dict[str, Any]:
        ...

    def validate(
        self,
        schema: type[_SchemaT] | dict[str, Any],
        data: dict[str, Any],
        *,
        coerce: object = _MISSING,
        max_depth: object = _MISSING,
        unknown_keys: object = _MISSING,
        error_mode: object = _MISSING,
    ) -> _SchemaT | dict[str, Any]:
        use_coerce = self.coerce if coerce is _MISSING else coerce
        use_max_depth = self.max_depth if max_depth is _MISSING else max_depth
        use_unknown_keys = self.unknown_keys if unknown_keys is _MISSING else unknown_keys
        use_error_mode = self.error_mode if error_mode is _MISSING else error_mode
        return validate(
            schema,
            data,
            coerce=cast(bool, use_coerce),
            max_depth=cast(int, use_max_depth),
            unknown_keys=cast(UnknownKeysMode, use_unknown_keys),
            error_mode=cast(ErrorMode, use_error_mode),
        )
