# Released, planned, and experimental

Feature availability separated from unreleased source work and proposed designs.

HTML: https://zodify.dev/roadmap/

Released zodify 0.8.0; Python >=3.10; alpha. Release manifest verified 2026-09-09.

## Released: 0.8.0

The verified 0.8.0 release provides validate, Optional, Validator, Schema, env, load_env, ValidationError and ValidationIssue. It preserves legacy structured issues and adds canonical details, strict JSON object input via zodify.json_io.validate_json, and conservative exact export via zodify.json_schema.export_json_schema and the root to_json_schema facade.

- [PyPI release](https://pypi.org/project/zodify/0.8.0/)
- [Current reference](https://zodify.dev/docs/)

## Proposed features

Compilation and rich reports remain unavailable. Approximate export, native execution and source generation remain outside the current scope; future work requires separate semantic, evidence and release gates.

Compilation requires an actual repeated-use workload and measured preparation economics before any public API is admitted. Version 0.8.0 is an alpha release. API stability is still being evaluated.

- [Development repository](https://github.com/junyoung2015/zodify)
- [Changelog](https://zodify.dev/changelog/)

## Scope

Zodify validates ordinary Python data. Use a recursive model framework or general JSON Schema validator when your application needs those capabilities.

Updated 2026-09-09. [Project source](https://github.com/junyoung2015/zodify).
