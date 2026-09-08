#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

if ! git rev-parse --show-toplevel >/dev/null 2>&1; then
  echo "error: release preflight must run inside a git worktree" >&2
  exit 1
fi

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
TMP_BASE="${TMPDIR:-$PWD/.tmp}"
mkdir -p "${TMP_BASE}"
WORK_DIR="$(mktemp -d "${TMP_BASE}/zodify-release-${TAG}.XXXXXX")"
DIST_DIR="${WORK_DIR}/dist"
RELEASE_NOTES_PATH="${WORK_DIR}/RELEASE_NOTES-${TAG}.md"
trap 'rm -rf "${WORK_DIR}"' EXIT

if git rev-parse --verify --quiet "refs/tags/${TAG}" >/dev/null; then
  echo "error: tag ${TAG} already exists" >&2
  exit 1
fi

./scripts/prepare_release_notes.sh "${TAG}" "${RELEASE_NOTES_PATH}"

if ! python -c "import build" >/dev/null 2>&1; then
  echo "error: python package 'build' is required. install with: python -m pip install build" >&2
  exit 1
fi

if ! python -m twine --version >/dev/null 2>&1; then
  echo "error: python package 'twine' is required. install with: python -m pip install twine" >&2
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

python scripts/check_public_repo_policy.py
python -m pytest tests/ -v
python -m pytest --doctest-modules zodify/
python -m pytest -q tests/test_logic_loc_budget.py
python -m mypy
python -m pyright
python -m build --sdist --wheel --outdir "${DIST_DIR}"
python scripts/check_package_artifacts.py "${DIST_DIR}"
python -m twine check "${DIST_DIR}"/*

echo
echo "preflight passed for ${TAG}"
echo "next:"
echo "  Confirm the Actions pause has ended and package publication is authorized."
echo "  git tag ${TAG}"
echo "  git push origin ${TAG}"
