"""Runtime coverage for the public load_env() API."""

import os
from pathlib import Path

import pytest

import zodify
from zodify import Schema, ValidationError, Validator, load_env, validate


def _write_env(tmp_path: Path, content: str | bytes, name: str = ".env") -> Path:
    path = tmp_path / name
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")
    return path


def _issue(path: Path, line: int, message: str, raw: str) -> dict[str, str]:
    return {
        "path": f"{path.resolve()}[line {line}]",
        "message": message,
        "expected": "valid .env assignment",
        "got": raw,
    }


def test_load_env_exported_in_dunder_all() -> None:
    assert "load_env" in zodify.__all__


def test_load_env_private_helpers_stay_out_of_public_namespace() -> None:
    assert not hasattr(zodify, "parse_env_file")
    assert not hasattr(zodify, "resolve_env_path")


def test_load_env_raw_mode_parses_supported_syntax_and_preserves_order(
    tmp_path: Path,
) -> None:
    path = _write_env(
        tmp_path,
        "\n".join(
            [
                "  # ignore comment lines whose first non-whitespace char is #",
                "API.KEY-NAME = spaced value  ",
                'QUOTED =   " keep # and ${VAR} = literal "   ',
                r"SINGLE='line\nvalue'",
                "EMPTY=",
                "URL = https://example.com?a=1#frag",
                "API.KEY-NAME = override",
            ]
        ),
    )

    result = load_env(path)

    assert result == {
        "API.KEY-NAME": "override",
        "QUOTED": " keep # and ${VAR} = literal ",
        "SINGLE": r"line\nvalue",
        "EMPTY": "",
        "URL": "https://example.com?a=1#frag",
    }
    assert list(result) == ["API.KEY-NAME", "QUOTED", "SINGLE", "EMPTY", "URL"]


def test_load_env_preserves_literal_inner_quotes_inside_matching_outer_quotes(
    tmp_path: Path,
) -> None:
    path = _write_env(tmp_path, 'KEY="a""\nOTHER=\'a\'\'\n')

    assert load_env(path) == {"KEY": 'a"', "OTHER": "a'"}


def test_load_env_allows_quotes_inside_unquoted_literal_values(
    tmp_path: Path,
) -> None:
    path = _write_env(tmp_path, 'CITY=O\'Hare\nJSON={"a":"b"}\n')

    assert load_env(path) == {"CITY": "O'Hare", "JSON": '{"a":"b"}'}


def test_load_env_uses_default_dotenv_from_cwd_and_does_not_mutate_os_environ(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_env(tmp_path, "PORT=9000\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PORT", "5000")

    result = load_env()

    assert result == {"PORT": "9000"}
    assert os.environ["PORT"] == "5000"


def test_load_env_readme_raw_example_smoke(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_env(tmp_path, "PORT=8080\nDEBUG=yes\n", "app.env")
    monkeypatch.chdir(tmp_path)

    raw = load_env("app.env")

    assert raw == {"PORT": "8080", "DEBUG": "yes"}


def test_load_env_readme_schema_example_smoke(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_env(tmp_path, "PORT=8080\nDEBUG=yes\n", "app.env")
    monkeypatch.chdir(tmp_path)

    config = load_env(
        "app.env",
        schema={"PORT": int, "DEBUG": bool},
    )

    assert config == {"PORT": 8080, "DEBUG": True}


def test_load_env_readme_validator_example_smoke(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_env(tmp_path, "PORT=8080\nEXTRA=drop-me\n", "app.env")
    monkeypatch.chdir(tmp_path)
    validator = Validator(coerce=False, unknown_keys="reject")
    raw = load_env("app.env")

    config = validator.validate(
        {"PORT": int},
        raw,
        coerce=True,
        max_depth=32,
        unknown_keys="strip",
    )

    assert config == {"PORT": 8080}


def test_load_env_bom_is_preserved_and_fails_first_key_validation(
    tmp_path: Path,
) -> None:
    path = _write_env(tmp_path, b"\xef\xbb\xbfPORT=5432\nOTHER=ok\n")

    with pytest.raises(ValueError) as exc_info:
        load_env(path)

    assert str(exc_info.value) == f"{path.resolve()}[line 1]: invalid key"


def test_load_env_preserves_unicode_line_separator_inside_physical_line(
    tmp_path: Path,
) -> None:
    path = _write_env(tmp_path, "KEY=a\u2028b\nOTHER=ok\n")

    assert load_env(path) == {"KEY": "a\u2028b", "OTHER": "ok"}


def test_load_env_text_parse_failures_are_newline_joined_in_file_order(
    tmp_path: Path,
) -> None:
    path = _write_env(tmp_path, "BROKEN\n1BAD=value\n")

    with pytest.raises(ValueError) as exc_info:
        load_env(path)

    assert str(exc_info.value) == "\n".join(
        [
            f"{path.resolve()}[line 1]: missing '='",
            f"{path.resolve()}[line 2]: invalid key",
        ]
    )


def test_load_env_reports_unsupported_syntax_for_nul_bytes(
    tmp_path: Path,
) -> None:
    path = _write_env(tmp_path, b"KEY=ok\x00value\n")

    with pytest.raises(ValueError) as exc_info:
        load_env(path)

    assert str(exc_info.value) == (
        f"{path.resolve()}[line 1]: unsupported .env syntax"
    )


def test_load_env_aggregates_structured_parse_failures_and_skips_schema_validation(
    tmp_path: Path,
) -> None:
    path = _write_env(
        tmp_path,
        "\n".join(
            [
                "BROKEN",
                " =value",
                "1BAD=value",
                "export KEY=value",
                'OPEN="value',
                "PORT=bad",
                "TAIL='x' tail",
            ]
        ),
    )

    with pytest.raises(ValidationError) as exc_info:
        load_env(path, schema={"PORT": int}, error_mode="structured")

    assert exc_info.value.issues == [
        _issue(path, 1, "missing '='", "BROKEN"),
        _issue(path, 2, "blank key", " =value"),
        _issue(path, 3, "invalid key", "1BAD=value"),
        _issue(path, 4, "export syntax is unsupported", "export KEY=value"),
        _issue(path, 5, "multiline values are unsupported", 'OPEN="value'),
        _issue(path, 7, "unmatched surrounding quote", "TAIL='x' tail"),
    ]


@pytest.mark.parametrize(
    ("line", "message"),
    [
        ('TAIL="x"tail"', "unmatched surrounding quote"),
        ('TAIL="x"tail', "unmatched surrounding quote"),
        ("TAIL='x'tail'", "unmatched surrounding quote"),
        ('TAIL=tail"x"', "unmatched surrounding quote"),
        ("TAIL='x' tail", "unmatched surrounding quote"),
        ('TAIL="x\'', "unmatched surrounding quote"),
    ],
)
def test_load_env_rejects_same_line_quote_mismatches(
    tmp_path: Path,
    line: str,
    message: str,
) -> None:
    path = _write_env(tmp_path, f"{line}\n")

    with pytest.raises(ValueError) as exc_info:
        load_env(path)

    assert str(exc_info.value) == f"{path.resolve()}[line 1]: {message}"


def test_load_env_missing_file_modes_follow_contract(tmp_path: Path) -> None:
    path = tmp_path / "missing.env"

    with pytest.raises(FileNotFoundError) as text_exc:
        load_env(path)
    assert str(path.resolve()) in str(text_exc.value)

    with pytest.raises(ValidationError) as structured_exc:
        load_env(path, error_mode="structured")
    assert structured_exc.value.issues == [
        {
            "path": f"{path.resolve()}[missing]",
            "message": "file not found",
            "expected": "existing .env file",
            "got": "missing path",
        }
    ]

    assert load_env(path, on_missing="empty") == {}

    with pytest.raises(ValueError, match="PORT: missing required key"):
        load_env(path, schema={"PORT": int}, on_missing="empty")


def test_load_env_non_missing_io_failures_propagate_unchanged(
    tmp_path: Path,
) -> None:
    with pytest.raises(IsADirectoryError):
        load_env(tmp_path)

    invalid_utf8 = _write_env(tmp_path, b"\xff", "invalid.env")
    with pytest.raises(UnicodeDecodeError):
        load_env(invalid_utf8)


def test_load_env_rejects_export_syntax_with_tab_whitespace(
    tmp_path: Path,
) -> None:
    path = _write_env(tmp_path, "export\tKEY=value\n")

    with pytest.raises(ValueError) as exc_info:
        load_env(path)

    assert str(exc_info.value) == (
        f"{path.resolve()}[line 1]: export syntax is unsupported"
    )


def test_load_env_raw_mode_rejects_schema_only_kwargs_before_file_parsing(
    tmp_path: Path,
) -> None:
    path = tmp_path / "missing.env"

    with pytest.raises(TypeError) as exc_info:
        load_env(path, coerce=True)

    assert str(exc_info.value) == (
        "schema is required when using coerce, max_depth, or unknown_keys"
    )


def test_load_env_raw_mode_schema_only_kwargs_precede_on_missing_validation(
    tmp_path: Path,
) -> None:
    path = tmp_path / "missing.env"

    with pytest.raises(TypeError) as exc_info:
        load_env(path, coerce=True, on_missing="bad")  # type: ignore[arg-type]

    assert str(exc_info.value) == (
        "schema is required when using coerce, max_depth, or unknown_keys"
    )


def test_load_env_requires_keyword_only_parameters_after_path(
    tmp_path: Path,
) -> None:
    path = _write_env(tmp_path, "PORT=9000\n")

    with pytest.raises(TypeError):
        load_env(path, "structured")  # type: ignore[call-arg]


def test_load_env_dict_schema_parity_matches_validate_with_explicit_overrides(
    tmp_path: Path,
) -> None:
    path = _write_env(tmp_path, "PORT=8080\nDEBUG=yes\nEXTRA=drop-me\n")
    schema = {"PORT": int, "DEBUG": bool}
    raw = load_env(path)

    assert load_env(
        path,
        schema=schema,
        coerce=True,
        max_depth=32,
        unknown_keys="strip",
    ) == validate(
        schema,
        raw,
        coerce=True,
        max_depth=32,
        unknown_keys="strip",
    )

    with pytest.raises(ValidationError) as load_env_exc:
        load_env(
            path,
            schema=schema,
            coerce=False,
            unknown_keys="strip",
            error_mode="structured",
        )

    with pytest.raises(ValidationError) as validate_exc:
        validate(
            schema,
            raw,
            coerce=False,
            unknown_keys="strip",
            error_mode="structured",
        )

    assert load_env_exc.value.issues == validate_exc.value.issues


def test_load_env_forwards_non_default_schema_mode_overrides(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = _write_env(tmp_path, "PORT=8080\nEXTRA=drop-me\n")
    captured: dict[str, object] = {}
    original_validate = zodify.validate

    def _spy_validate(schema: object, data: dict[str, object], **kwargs: object) -> dict[str, object]:
        captured["schema"] = schema
        captured["data"] = dict(data)
        captured["kwargs"] = dict(kwargs)
        return original_validate(schema, data, **kwargs)

    monkeypatch.setattr(zodify, "validate", _spy_validate)

    with pytest.raises(ValueError, match="EXTRA: unknown key"):
        load_env(
            path,
            schema={"PORT": int},
            coerce=False,
            max_depth=7,
            unknown_keys="reject",
            error_mode="text",
        )

    assert captured == {
        "schema": {"PORT": int},
        "data": {"PORT": "8080", "EXTRA": "drop-me"},
        "kwargs": {
            "coerce": False,
            "max_depth": 7,
            "unknown_keys": "reject",
            "error_mode": "text",
        },
    }


def test_load_env_schema_input_returns_schema_wrapper_type(
    tmp_path: Path,
) -> None:
    class AppConfig(Schema):
        port: int
        debug: bool

    path = _write_env(tmp_path, "port=8080\ndebug=yes\nextra=drop-me\n")

    result = load_env(path, schema=AppConfig)

    assert isinstance(result, AppConfig)
    assert result.port == 8080
    assert result.debug is True
    assert "extra" not in result


def test_validator_validate_composition_keeps_validator_defaults_until_overridden(
    tmp_path: Path,
) -> None:
    path = _write_env(tmp_path, "port=8080\nextra=drop-me\n")
    schema = {"port": int}
    raw = load_env(path)
    validator = Validator(coerce=False, unknown_keys="reject")

    with pytest.raises(ValueError) as exc_info:
        validator.validate(schema, raw)

    assert str(exc_info.value) == "port: expected int, got str\nextra: unknown key"
    assert validator.validate(
        schema,
        raw,
        coerce=True,
        unknown_keys="strip",
    ) == load_env(path, schema=schema)


def test_load_env_on_missing_empty_schema_mode_continues_in_structured_mode(
    tmp_path: Path,
) -> None:
    path = tmp_path / "missing.env"
    schema = {"PORT": int}

    with pytest.raises(ValidationError) as load_env_exc:
        load_env(path, schema=schema, on_missing="empty", error_mode="structured")

    with pytest.raises(ValidationError) as validate_exc:
        validate(
            schema,
            {},
            coerce=True,
            max_depth=32,
            unknown_keys="strip",
            error_mode="structured",
        )

    assert load_env_exc.value.issues == validate_exc.value.issues
