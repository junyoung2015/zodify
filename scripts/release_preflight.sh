#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

PYPROJECT_VERSION="$(sed -nE 's/^version = "([^"]+)"/\1/p' pyproject.toml | head -n 1)"
MODULE_VERSION="$(sed -nE 's/^__version__(:[[:space:]]*[^=]+)?[[:space:]]*=[[:space:]]*"([^"]+)".*/\2/p' zodify/__init__.py | head -n 1)"
TEST_VERSION="$(sed -nE 's/^[[:space:]]*assert __version__ == "([^"]+)".*/\1/p' tests/test_zodify.py | head -n 1)"

if [[ -z "${PYPROJECT_VERSION}" || -z "${MODULE_VERSION}" || -z "${TEST_VERSION}" ]]; then
  echo "error: could not read release version triad (pyproject.toml, zodify/__init__.py, tests/test_zodify.py)" >&2
  exit 1
fi

if [[ "${PYPROJECT_VERSION}" != "${MODULE_VERSION}" ]]; then
  echo "error: version mismatch" >&2
  echo "  pyproject.toml: ${PYPROJECT_VERSION}" >&2
  echo "  zodify/__init__.py: ${MODULE_VERSION}" >&2
  exit 1
fi

if [[ "${PYPROJECT_VERSION}" != "${TEST_VERSION}" ]]; then
  echo "error: version mismatch" >&2
  echo "  pyproject.toml: ${PYPROJECT_VERSION}" >&2
  echo "  tests/test_zodify.py: ${TEST_VERSION}" >&2
  exit 1
fi

TAG="v${PYPROJECT_VERSION}"

if git rev-parse "${TAG}" >/dev/null 2>&1; then
  echo "error: tag ${TAG} already exists" >&2
  exit 1
fi

./scripts/extract_changelog_section.sh "${TAG}" CHANGELOG.md /tmp/RELEASE_NOTES-"${TAG}".md

if ! python -c "import build" >/dev/null 2>&1; then
  echo "error: python package 'build' is required. install with: python -m pip install build" >&2
  exit 1
fi

if ! command -v mypy >/dev/null 2>&1; then
  echo "error: command 'mypy' not found. install with: python -m pip install mypy" >&2
  exit 1
fi

if ! command -v pyright >/dev/null 2>&1; then
  echo "error: command 'pyright' not found. install with: python -m pip install pyright" >&2
  exit 1
fi

if [[ -n "$(git status --porcelain)" ]]; then
  echo "error: working tree has uncommitted changes; commit or stash before release preflight" >&2
  exit 1
fi

python -m pytest tests/ -v
python -m pytest --doctest-modules zodify/
python -m pytest -q tests/test_logic_loc_budget.py
mypy --strict zodify/
pyright zodify/
python -m build

echo
echo "preflight passed for ${TAG}"
echo "next:"
echo "  git tag ${TAG}"
echo "  git push origin ${TAG}"
