# Schema Class Feasibility Report

Date: 2026-03-06
Decision: `NO-GO`

## Summary

Class-based schema syntax was prototyped and validated against runtime and typing behavior.
The prototype is technically feasible, but it is not approved for implementation in the current roadmap phase.

Primary blocker:

- projected complexity footprint measured as `199` logic LOC versus a `< 80` acceptance threshold for this proposal.

## Key Evidence

- Runtime normalization is proven for both entry points:
  - `validate(MySchema, data)` delegates a plain dict schema to `zodify.validate(...)`
  - `Validator().validate(MySchema, data)` delegates a plain dict schema to `zodify.validate(...)`
- Dict compatibility behavior is preserved for schema-class results:
  - `isinstance(result, dict)`
  - `json.dumps(result)`
  - `dict(result)`
  - `**result` unpacking
- Plain dict schemas still return plain `dict`.
- Typing contract checks pass with both mypy and pyright:
  - `validate(MySchema, data) -> MySchema`
  - `Validator().validate(MySchema, data) -> MySchema`

## Canonical Tracked Files

This repository keeps planning workflow artifacts local-only. The canonical tracked evidence for this decision is:

- `notes/architecture/schema-class-feasibility-report.md`
- `tests/typing/schema_class_runtime_prototype.py`
- `tests/test_schema_class_runtime_spike.py`
- `tests/typing/test_schema_class_typing_contract.py`

## Next Action

Do not start schema-class implementation yet.

If the team wants to revisit the feature, open a redesign spike focused on extraction into `zodify/schema.py` while preserving the existing public API surface.
