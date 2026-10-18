# About zodify

The project's origin, author, and scope.

HTML: https://zodify.dev/about/

Released zodify 0.8.1; Python >=3.10; alpha. Release manifest verified 2026-10-18.

## A validator for a small script

Jun Young Sohn (jusohn) created zodify while working on a small automation script involving environment variables and API keys. The original project account describes a roughly 20-line script and the wish for validation that fit its scale.

That led to a dict-first interface: describe expected values with Python types and validate the dict at the boundary. Optional Schema declarations later added attribute access over the same engine.

- [Project repository](https://github.com/junyoung2015/zodify)
- [Try it](https://zodify.dev/docs/getting-started/)

## Project scope

Zodify has zero required runtime dependencies and uses ordinary Python data shapes with optional coercion. Zod inspired the original interface. Zodify has its own Python API and is maintained independently. The project uses the MIT license.

Other tools solve broader problems. The selection guide explains where TypeAdapter or a JSON Schema implementation may serve your application better.

- [Selection guide](https://zodify.dev/compare/)
- [Roadmap](https://zodify.dev/roadmap/)

Updated 2026-09-09. [Project source](https://github.com/junyoung2015/zodify).
