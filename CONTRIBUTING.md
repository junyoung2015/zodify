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

The local gates include fatal lint, runtime tests and doctests, both type checkers,
installed-artifact checks, package metadata validation, and the static site build.
`pytest tests/ -q` covers the public test surface;
`tests/test_logic_loc_budget.py` enforces shipped runtime LOC budgets.
`benchmarks/equivalent.py` checks equivalent positive and negative fixtures before
timing strict dictionary output. Historical comparison scripts do not establish
a general speed ranking.

For publication, follow the [local release procedure](release-notes/RELEASING.md).
Obtain the owner's release decision before uploading the retained artifacts with
Twine, then verify downloaded PyPI hashes and an independent install before the
matching tag, final GitHub Release, or availability changes. Recheck budget and
reconcile publishing workflows before enabling Actions; the calendar alone does
not enable publication. Production Pages uses locally verified static files and
`.nojekyll` on the Pages source branch.

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
