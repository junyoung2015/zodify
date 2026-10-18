# Released, planned, and experimental

Feature availability separated from unreleased source work and proposed designs.

HTML: https://zodify.dev/roadmap/

Released zodify 0.8.1; Python >=3.10; alpha. Release manifest verified 2026-10-18.

## Released: 0.8.1

The verified 0.8.1 release provides validate, Optional, Validator, Schema, env, load_env, ValidationError and ValidationIssue. It preserves legacy structured issues and the 0.8.0 canonical details, strict JSON object input via zodify.json_io.validate_json, and conservative exact export via zodify.json_schema.export_json_schema and the root to_json_schema facade.

Version 0.8.1 fixes class-schema field discovery under Python 3.14 deferred annotations. Fresh PyPI wheel installs passed the installed contract and examples on macOS CPython 3.10.19 and 3.14.6. The declared support range remains Python 3.10–3.13; these checks do not claim broader Python 3.14, operating-system, free-threaded, or JIT support.

- [0.8.1 release notes](https://github.com/junyoung2015/zodify/blob/main/release-notes/v0.8.1.md)
- [PyPI release](https://pypi.org/project/zodify/0.8.1/)
- [Current reference](https://zodify.dev/docs/)

## Proposed features

Compilation and rich reports remain unavailable. Approximate export, native execution and source generation remain outside the current scope; future work requires separate semantic, evidence and release gates.

Compilation requires an actual repeated-use workload and measured preparation economics before any public API is admitted. Version 0.8.1 is an alpha release. API stability is still being evaluated.

- [Development repository](https://github.com/junyoung2015/zodify)
- [Changelog](https://zodify.dev/changelog/)

## Scope

Zodify validates ordinary Python data. Use a recursive model framework or general JSON Schema validator when your application needs those capabilities.

Updated 2026-10-18. [Project source](https://github.com/junyoung2015/zodify).
