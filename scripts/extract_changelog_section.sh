#!/usr/bin/env bash
set -euo pipefail

TAG="${1:-}"
CHANGELOG_PATH="${2:-CHANGELOG.md}"
OUTPUT_PATH="${3:-RELEASE_NOTES.md}"

if [[ -z "${TAG}" ]]; then
  echo "usage: $0 <tag> [changelog-path] [output-path]" >&2
  exit 2
fi

if [[ ! -f "${CHANGELOG_PATH}" ]]; then
  echo "error: changelog file not found: ${CHANGELOG_PATH}" >&2
  exit 1
fi

if ! grep -qE "^## \\[${TAG//./\\.}\\]" "${CHANGELOG_PATH}"; then
  echo "error: no changelog section found for tag ${TAG} in ${CHANGELOG_PATH}" >&2
  exit 1
fi

awk -v tag="${TAG}" '
  BEGIN {
    capture = 0
  }
  $0 ~ "^## \\[" tag "\\]" {
    capture = 1
  }
  capture && $0 ~ "^## \\[" && $0 !~ "^## \\[" tag "\\]" {
    exit
  }
  capture {
    print
  }
' "${CHANGELOG_PATH}" > "${OUTPUT_PATH}"

if ! grep -qE "[^[:space:]]" "${OUTPUT_PATH}"; then
  echo "error: extracted changelog section is empty for tag ${TAG}" >&2
  exit 1
fi

echo "release notes extracted for ${TAG} -> ${OUTPUT_PATH}"
