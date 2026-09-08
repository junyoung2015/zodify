#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON="${PYTHON:-$PWD/.venv/bin/python}"
"$PYTHON" -m flake8 zodify/ tests/ --select=E9,F63,F7,F82 --show-source
"$PYTHON" -m pytest tests/ -q
"$PYTHON" -m pytest --doctest-modules zodify/ -q
"$PYTHON" -m mypy
"$PYTHON" -m pyright
"$PYTHON" scripts/check_public_repo_policy.py
dist_dir="$(mktemp -d "${TMPDIR:-/tmp}/zodify-dist.XXXXXX")"
trap 'rm -rf "$dist_dir"' EXIT
"$PYTHON" -m build --sdist --wheel --outdir "$dist_dir"
"$PYTHON" scripts/check_package_artifacts.py "$dist_dir"
"$PYTHON" -m twine check "$dist_dir"/*
(cd site && npm ci && npm run lint && npm run build)
