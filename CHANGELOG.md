# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

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
