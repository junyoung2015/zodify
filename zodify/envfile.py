"""Private helpers for deterministic .env file parsing."""

from __future__ import annotations

import os
import re
from pathlib import Path

_ENV_KEY_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_.-]*\Z")
_ENV_EXPECTED = "valid .env assignment"


def resolve_env_path(path: str | os.PathLike[str]) -> Path:
    return Path(path).resolve()


def _iter_env_lines(text: str) -> list[str]:
    lines = text.split("\n")
    if text.endswith("\n"):
        lines.pop()
    return [line[:-1] if line.endswith("\r") else line for line in lines]


def parse_env_file(
    path: Path,
) -> tuple[dict[str, str], list[tuple[str, str, str, str]]]:
    data: dict[str, str] = {}
    issues: list[tuple[str, str, str, str]] = []
    for line_number, raw_line in enumerate(_iter_env_lines(path.read_text(encoding="utf-8")), start=1):
        stripped = raw_line.lstrip()
        if not stripped or stripped.startswith("#"): continue
        message: str | None = None
        if "\x00" in raw_line: message = "unsupported .env syntax"
        elif "=" not in raw_line: message = "missing '='"
        else:
            key, value = raw_line.split("=", 1); key = key.strip(); value = value.strip()
            if key == "": message = "blank key"
            elif key.startswith("export") and key[6:7].isspace(): message = "export syntax is unsupported"
            elif _ENV_KEY_RE.fullmatch(key) is None: message = "invalid key"
            elif value == "": data[key] = ""; continue
            elif value[0] in "\"'":
                quote = value[0]
                if len(value) == 1: message = "multiline values are unsupported"
                elif value[-1] == quote:
                    inner = value[1:-1]
                    if quote in inner.rstrip(quote): message = "unmatched surrounding quote"
                    else: data[key] = inner; continue
                elif value[-1] in "\"'" or quote in value[1:]: message = "unmatched surrounding quote"
                else: message = "multiline values are unsupported"
            elif value[-1] in "\"'": message = "unmatched surrounding quote"
            else: data[key] = value; continue
        issues.append((f"{path}[line {line_number}]", message, _ENV_EXPECTED, raw_line))
    return data, issues
