# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [v0.5.0] - 2026-03-06

### Added

- Added `Validator` class with reusable default configuration (`coerce`, `max_depth`, `unknown_keys`, `error_mode`) and per-call overrides.
- Added comprehensive `tests/test_validator_class.py` coverage for defaults, override non-mutation, multi-instance isolation, and parity with bare `validate()`.
- Added README `Configuration` section documenting `Validator` usage and call-level override patterns while retaining bare `validate()` as the recommended starting point.

### Changed

- Refactored mode-option validation into shared internal helper logic to keep `validate()` and `Validator` option contracts aligned.
- Updated static typing configuration for pyright package-targeted checks (`[tool.pyright] include = ["zodify"]`).
- Updated benchmark comparison harness to use zodify's dict-schema API directly.

## [v0.4.1] - 2026-03-04

### Added

- Added six runnable example scripts in `examples/`: `basic_validation.py`, `nested_schemas.py`, `custom_validators.py`, `union_types.py`, `env_config.py`, and `structured_errors.py`.
- Added `tests/test_examples.py` smoke coverage for required example presence, runnable entrypoints, expected-output verification, and runtime API usage checks.
- Added public API export parity assertion to keep `__version__` included in `zodify.__all__`.
- Added package-boundary verification policy for examples (wheel excludes runtime examples; source distribution may include them for documentation visibility).
- Added README `Schema Composition` section showing plain-dict schema reuse, nested composition, nested union member usage, and a runnable reference to `examples/nested_schemas.py`.
- Added README consistency updates: `Schema composition` comparison-table row, roadmap status aligned to `v0.4.1`, and release tagging example updated to `git tag v0.4.1`.

## [v0.4.0] - 2026-03-02

### Added

- `ValidationError` exception class: subclasses `ValueError` with `.issues` attribute containing structured `list[dict]` of validation failures. Each issue dict has `path`, `message`, `expected`, and `got` keys.
- `error_mode` parameter on `validate()`: `error_mode="structured"` raises `ValidationError` with machine-readable `.issues`; default `error_mode="text"` preserves existing `ValueError` string behavior.
- Structured error output covers all error types including union mismatch (`str | int`), coercion failure, custom validator failure, depth exceeded, and unknown key errors.
- copy/deepcopy/pickle support for `ValidationError` via `__reduce__`.

## [v0.3.0] - 2026-03-02

### Added

- Union type support: `str | int` runtime schema syntax for validating values against multiple types.
- Union coercion with left-to-right priority: when `coerce=True`, union members are tried in declaration order - first exact match (non-str types), then coercion attempts. First success wins.

### Known Limitations

- `str` catch-all in union coercion: when `str` is a union member and `coerce=True`, any value that fails earlier union members will fall through to `str()` coercion (e.g., `int | str` with `True` produces `"True"`). Place `str` last in unions to use it as a fallback.

## [v0.2.1] - 2026-03-01

### Added

- PEP 561 `py.typed` marker file for type checker recognition.
- Inline type annotations on all public and internal symbols.
- `@overload` signatures for `env()` enabling IDE type inference (e.g., `env("PORT", int)` infers `int`).
- Google-style docstrings with usage examples on all public API symbols (`validate`, `env`, `Optional`).
- mypy (strict mode) and pyright CI gates as merge-blocking checks.

### Changed

- Internal function docstrings (`_coerce_value`, `_check_value`, `_validate`) trimmed to one-line per architecture pattern.
- flake8 CI step changed to report-only (`--exit-zero`) - type checkers now handle correctness gating.

### Known Limitations

- `Optional` default values are **not type-checked**. `Optional(int, "text")` will use the string default without validation. Verify your defaults match the expected type.
- When `coerce=True` with target type `str`, any value is accepted via Python's `str()` builtin (e.g., `str(None)` becomes `"None"`). Non-string targets require string input for coercion.

## [v0.2.0] - 2026-02-27

### Added

- `max_depth` parameter on `validate()` with default of 32 to prevent stack overflow from deeply nested data.
- Custom validator functions: use any callable (lambda or function) as a schema value for value-level validation beyond type checking.
- `unknown_keys` parameter on `validate()` with default `"reject"` to control handling of extra keys in data. Use `"strip"` for previous silent-ignore behavior.
- Performance benchmark scripts (`benchmarks/`) for compliance verification: import time, validate speed, env overhead.

### Changed

- Internal error representation refactored from format strings to structured 4-tuples `(path, message, expected, got)` for future structured error support.
- `validate()` parameters after `data` are now keyword-only (enforced via `*`).
- `test_env.py` extracted from `test_zodify.py` for cleaner test organization.
- Unknown keys in data are now rejected by default. Use `unknown_keys="strip"` to restore v0.1.0 behavior.
- CI pipeline now includes benchmark reporting on Python 3.12 (non-gating).

## [v0.1.0] - 2026-02-25

### Added

- Nested dict schema validation with recursive validation and dot-path errors (for example, `db.port`).
- `Optional` schema marker with optional defaults for missing keys.
- List element typing via single-element schema lists (for example, `{"tags": [str]}`), including nested list-of-dict support.
- Broader automated test coverage for nested schemas, optionals, list validation, and coercion edge cases.

### Changed

- Updated README with v0.1.0 examples for nested dicts, optional keys, and list element validation.
- Updated package metadata and versioning to `0.1.0`.

### Fixed

- CI/publish workflow robustness for install/test/build flow and release handling.
- Packaging metadata cleanup in `pyproject.toml` (license format/classifier cleanup).

## [v0.0.1] - 2026-02-25

### Added

- Initial public release of `zodify`.
- Core `validate()` API for dict schema validation with strict type checks.
- `coerce=True` support for string coercion into `str`, `int`, `float`, and `bool`.
- `env()` helper for typed environment variable loading with optional defaults.
- Aggregated validation errors in a single `ValueError`.
- Zero-dependency, single-file library design.
