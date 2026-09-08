#!/usr/bin/env python3
"""Fail when tracked repo paths or text contain restricted public vocabulary."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


def _build_terms() -> tuple[str, ...]:
    word_parts = (
        ("bm", "ad"),
        ("ep", "ic"),
        ("st", "ory"),
        ("st", "ories"),
        ("nf", "r"),
        ("f", "r"),
    )
    phrase_parts = (
        ("func", "tional", " ", "require", "ments"),
        ("non", "-", "func", "tional", " ", "require", "ments"),
    )
    return tuple("".join(parts) for parts in word_parts + phrase_parts)


TERMS = _build_terms()
TERM_PATTERN = re.compile(
    r"(?<![a-z0-9])(" + "|".join(re.escape(term) for term in TERMS) + r")(?![a-z0-9])",
    re.IGNORECASE,
)


def _tracked_paths() -> list[str]:
    output = subprocess.check_output(["git", "ls-files", "-z"], text=False)
    return [item.decode("utf-8") for item in output.split(b"\0") if item]


def _is_binary(path: Path) -> bool:
    try:
        chunk = path.read_bytes()
    except FileNotFoundError:
        return False
    return b"\0" in chunk


def _path_hits(paths: list[str]) -> list[str]:
    return [path for path in paths if TERM_PATTERN.search(path.lower())]


def _content_hits(paths: list[str]) -> list[str]:
    hits: list[str] = []
    for raw_path in paths:
        path = Path(raw_path)
        if _is_binary(path):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError as exc:
            hits.append(f"{raw_path}: read error: {exc}")
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            if TERM_PATTERN.search(line.lower()):
                snippet = line.strip()
                if len(snippet) > 160:
                    snippet = snippet[:157] + "..."
                hits.append(f"{raw_path}:{line_no}: {snippet}")
    return hits


def main() -> int:
    paths = _tracked_paths()
    bad_paths = _path_hits(paths)
    bad_content = _content_hits(paths)

    if not bad_paths and not bad_content:
        print("public repo policy check passed")
        return 0

    print("public repo policy check failed", file=sys.stderr)
    if bad_paths:
        print("path matches:", file=sys.stderr)
        for item in bad_paths:
            print(f"  {item}", file=sys.stderr)
    if bad_content:
        print("content matches:", file=sys.stderr)
        for item in bad_content:
            print(f"  {item}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
