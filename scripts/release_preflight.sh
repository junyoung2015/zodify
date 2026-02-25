#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

PYPROJECT_VERSION="$(sed -nE 's/^version = "([^"]+)"/\1/p' pyproject.toml | head -n 1)"
MODULE_VERSION="$(sed -nE 's/^__version__ = "([^"]+)"/\1/p' zodify/__init__.py | head -n 1)"

if [[ -z "${PYPROJECT_VERSION}" || -z "${MODULE_VERSION}" ]]; then
  echo "error: could not read versions from pyproject.toml and zodify/__init__.py" >&2
  exit 1
fi

if [[ "${PYPROJECT_VERSION}" != "${MODULE_VERSION}" ]]; then
  echo "error: version mismatch" >&2
  echo "  pyproject.toml: ${PYPROJECT_VERSION}" >&2
  echo "  zodify/__init__.py: ${MODULE_VERSION}" >&2
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

if [[ -n "$(git status --porcelain)" ]]; then
  echo "warning: working tree has uncommitted changes; preflight is running against local state" >&2
fi

python -m pytest tests/ -v
python -m build

echo
echo "preflight passed for ${TAG}"
echo "next:"
echo "  git tag ${TAG}"
echo "  git push origin ${TAG}"
