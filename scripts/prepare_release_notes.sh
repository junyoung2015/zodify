#!/usr/bin/env bash
set -euo pipefail

TAG="${1:-}"
OUTPUT_PATH="${2:-RELEASE_NOTES.md}"
CURATED_PATH="release-notes/${TAG}.md"

if [[ -z "${TAG}" ]]; then
  echo "usage: $0 <tag> [output-path]" >&2
  exit 2
fi

if [[ -f "${CURATED_PATH}" ]]; then
  cp "${CURATED_PATH}" "${OUTPUT_PATH}"
  echo "using curated release notes for ${TAG} -> ${OUTPUT_PATH}"
  exit 0
fi

./scripts/extract_changelog_section.sh "${TAG}" CHANGELOG.md "${OUTPUT_PATH}"
