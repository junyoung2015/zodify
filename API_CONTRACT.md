# Supported API and compatibility contract

This inventory describes the **unreleased 0.8.0 candidate** and the intended
scope for 1.0 stabilization. It does not announce a stable release. PyPI release
availability is verified separately from source version numbers.

## Public entry points

| Import | Contract |
| --- | --- |
| `zodify.validate` | Validate a dict against a dict schema or supported `Schema` declaration; return a new dict or the supported dict-compatible class result. |
| `zodify.Optional` | Mark a missing field optional, with an optional trusted default reference. Nullability is a separate type declaration. |
| `zodify.Validator` | Reuse validation options with explicit call overrides. Does not compile or cache schemas. |
| `zodify.Schema` | Optional class syntax for the documented runtime annotation subset; not arbitrary Python typing or a model lifecycle. |
| `zodify.env` | Read and convert one environment variable; missing defaults are trusted. |
| `zodify.load_env` | Parse a bounded-scope env file and optionally delegate validation; never mutate the process environment. |
| `zodify.ValidationError` | Structured validation error, compatible with `ValueError`, legacy construction, and legacy four-key engine issues. |
| `zodify.ValidationIssue` | Immutable canonical failure record with code, typed location, display path, message, expected and received labels. |
| `zodify.to_json_schema` | Document-returning facade for the exact export subset. |
| `zodify.json_schema.export_json_schema` | Export the exact supported input profile with explicit fidelity metadata. |
| `zodify.json_schema.JSONSchemaExport` | Result record; its document is a fresh caller-owned mutable mapping. |
| `zodify.json_schema.UnsupportedSchemaError` | Explicit export refusal with structural location and reason. |
| `zodify.json_io.validate_json` | Parse a text or UTF-8 byte JSON object under the documented parser policy, then delegate ordinary validation. |
| `zodify.json_io.JSONInputError` | Generic parser/root error with code and optional decoder line/column; separate from application validation. |
| `zodify.__version__` | Candidate/runtime version; does not establish publication. |

Internal helpers, private modules, generated class-result carriers, imported
typing names, and schema normalization internals are not extension interfaces.
Canonical record import and supported pickle compatibility must remain intact
if implementation modules move. No plugin ABI or public intermediate form exists.

## Behavior to preserve

- Exact built-in type checks distinguish `bool` from `int`. Ordinary validation
  defaults to no coercion and unknown-key rejection. `load_env(..., schema=...)`
  instead defaults to coercion and stripping unknown keys;
  union order and existing exact-match behavior remain characterized in tests.
- Missing and null are different. Defaults are neither validated nor copied;
  repeated results can share mutable defaults. Rebinding an ordinary schema or
  marker is visible on subsequent calls.
- Shaped dict/list results are rebuilt; values accepted through bare types and
  trusted defaults can remain shared. Successful validation is not a deep freeze.
- `max_depth` counts shaped dictionary traversals, including the root. It does not bound
  list nesting, parser allocation, callback execution time, or input size.
- Callbacks execute during the existing traversal, including after earlier
  validation failures. Preparation or diagnostics must not rerun callbacks.
- Invalid entries in plain dict schemas retain ordinary lazy error timing.
  `Schema` declarations check annotations eagerly at class definition. Adapters
  have their own documented parsing/preparation phases; do not silently normalize ordinary
  validation eagerly as an internal refactor.
- The supported interpreter matrix is Python 3.10–3.13. Add advertised support
  only after the runtime, typing and installed-artifact checks pass.

## Diagnostic contract

Text mode retains `ValueError` and existing text behavior. Structured mode retains
engine `.issues` dictionaries with exactly `path`, `message`, `expected`, and
`got`. Manual legacy construction continues accepting the old supplied shape.

`details` is a separate immutable tuple snapshot when structural information is
available. It is `None` for manual legacy errors, env parser errors, and failures
without a supported exact string/integer key location. Mutating `.issues` does
not mutate the canonical snapshot. Copy, deepcopy and pickle retain both views.

Current canonical codes: `type_mismatch`, `missing_key`, `unknown_key`,
`coercion_failed`, `custom_validation_failed`, `union_mismatch`, `depth_exceeded`.
Existing meanings and promised ordering must remain compatible. New codes can be
added; consumers must tolerate an unknown code. Human wording is not a machine
identifier. Preserve established legacy wording unless a migration says otherwise.

Canonical messages omit raw input and callback exception text. Keys and type
labels can still be sensitive; legacy messages and tracebacks can expose data.
This is not a universal safe-logging or sandbox guarantee.

## JSON boundaries

JSON input accepts only text/UTF-8 bytes and an object root. It rejects duplicate
keys, BOMs, nonfinite constants and float overflow. Optional `max_bytes` measures
UTF-8 bytes before parsing; counting text bytes allocates an encoded copy.
Decoder line/column comes from the active interpreter and may differ by version.

Export targets Draft 2020-12 over ordinary JSON-compatible built-in instances.
Only exact fidelity, strict validation, unknown-key rejection and the default
32-dictionary depth profile are supported. The separate structural preparation
cap is 64 transitions. Numeric types, defaults, bare containers, arbitrary
predicates, cycles and unsupported declarations are refused. The exporter is not
a general JSON Schema validator and does not describe transformations or raw
JSON parser policies. Its optional fields without defaults remain exportable.

## Release and migration policy

Before 1.0, every intentional change to accepted inputs, outputs, default
ownership, callback behavior, exception phase, public signatures or serialized
records requires a named decision, before/after examples, regression fixtures,
migration notes and independent review. Alpha status does not remove that duty.

After 1.0, preserve the named stable surface within 1.x. Breaking changes require
a major release with deprecation/migration guidance. Patch releases fix defects
without silently broadening acceptance. Adding a machine code is distinct from
changing an existing code's meaning. Never remove a shipped API to simplify an
experiment; a new experiment remains private until its own gates pass.

For the inherited unshipped exporter, 0.8.0 intentionally refuses numeric and
default mappings that earlier local drafts approximated. No earlier published
version provided those APIs. Compilation, reports, native execution, source
generation and approximate export remain outside the committed 1.0 scope unless
admitted separately with evidence.

1.0 additionally requires at least 14 calendar days of recorded candidate use,
upgrade and rollback evidence, owner release decision, verified published
artifacts, and matching production documentation. Neither test counts nor elapsed
time without observations establishes those gates.
