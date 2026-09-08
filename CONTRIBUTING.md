# Contributing to zodify

## Setup and local validation

Use Python 3.10–3.13 and Node 22.12 or later for the documentation build.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
./scripts/local_checks.sh
```

GitHub Actions is disabled through October 1, 2026, 09:00 Asia/Seoul. Record local
commands, interpreter versions and outcomes in the PR. A maintainer may publish
an accurate commit status from those checks; do not bypass a failing check.
Validate web changes by deploying the tested static artifact and checking the
production pages, missing-route HTTP status and no-JavaScript navigation.

## Compatibility and scope

Keep pure Python, zero required runtime dependencies and one validation engine.
Optional adapters live in focused modules. Preserve existing imports, class-schema
support and legacy error behavior. Characterize before changing semantics; document
intentional changes with concrete examples and migration advice. Defaults remain
trusted references and depth counts dictionary visits. Avoid unrelated formatting
or dependency upgrades. Public website claims must match the installed release.

## Submitting changes

Create a branch from main, implement one coherent change, and open a PR describing
the problem, resulting behavior and actual validation. Include negative cases for
semantic changes. Builds and merges do not establish package publication; release
facts change only after the published wheel is verified. Compilation and other
experiments need measured value and explicit contracts before becoming public.
