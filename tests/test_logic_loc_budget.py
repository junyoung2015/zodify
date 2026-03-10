"""Automated logic LOC budget checks for package footprint control."""

from __future__ import annotations

import ast
from pathlib import Path

SOURCE_PACKAGE = Path(__file__).resolve().parents[1] / "zodify"
SOURCE_FILE = SOURCE_PACKAGE / "__init__.py"
SCHEMA_FILE = SOURCE_PACKAGE / "schema.py"
MAX_LOGIC_LOC = 500
BASELINE_INIT_LOGIC_LOC = 260
MAX_INIT_LOGIC_DELTA_WITH_SCHEMA = 50
MAX_SCHEMA_LOGIC_LOC = 175


def _collect_docstring_lines(tree: ast.AST) -> set[int]:
    lines: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.body:
                continue
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
                if isinstance(first.value.value, str):
                    end = getattr(first, "end_lineno", first.lineno)
                    lines.update(range(first.lineno, end + 1))
    return lines


def _is_overload_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Name) and decorator.id == "overload":
            return True
    return False


def compute_logic_loc(path: Path) -> int:
    source = path.read_text(encoding="utf-8")
    lines = source.splitlines()
    tree = ast.parse(source)

    ignored_lines = _collect_docstring_lines(tree)

    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and node.value is None:
            end = getattr(node, "end_lineno", node.lineno)
            ignored_lines.update(range(node.lineno, end + 1))

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if _is_overload_function(node):
                start = min(
                    [node.lineno, *[d.lineno for d in node.decorator_list]],
                )
                end = getattr(node, "end_lineno", node.lineno)
                ignored_lines.update(range(start, end + 1))
                continue

            if node.body:
                header_end = node.body[0].lineno - 1
                if header_end > node.lineno:
                    ignored_lines.update(range(node.lineno + 1, header_end + 1))

    logic_loc = 0
    for lineno, line in enumerate(lines, start=1):
        if lineno in ignored_lines:
            continue
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        logic_loc += 1

    return logic_loc


def compute_package_logic_loc(package_dir: Path) -> int:
    return sum(
        compute_logic_loc(path)
        for path in sorted(package_dir.rglob("*.py"))
        if path.is_file()
    )


def test_logic_loc_budget_is_below_500_lines():
    logic_loc = compute_package_logic_loc(SOURCE_PACKAGE)
    assert logic_loc <= MAX_LOGIC_LOC, (
        f"package logic LOC budget exceeded: {logic_loc} > {MAX_LOGIC_LOC}"
    )


def test_init_logic_loc_stays_thin_when_schema_module_exists():
    if not SCHEMA_FILE.exists():
        return

    init_logic_loc = compute_logic_loc(SOURCE_FILE)
    allowed = BASELINE_INIT_LOGIC_LOC + MAX_INIT_LOGIC_DELTA_WITH_SCHEMA
    assert init_logic_loc <= allowed, (
        "zodify/__init__.py lost the approved thin-entrypoint shape: "
        f"{init_logic_loc} > {allowed}"
    )


def test_schema_module_logic_loc_stays_within_schema_module_budget():
    if not SCHEMA_FILE.exists():
        return

    schema_logic_loc = compute_logic_loc(SCHEMA_FILE)
    assert schema_logic_loc <= MAX_SCHEMA_LOGIC_LOC, (
        "zodify/schema.py exceeded the approved focused-module budget: "
        f"{schema_logic_loc} > {MAX_SCHEMA_LOGIC_LOC}"
    )
