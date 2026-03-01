"""Automated logic LOC budget checks for NFR5."""

from __future__ import annotations

import ast
from pathlib import Path

SOURCE_FILE = Path(__file__).resolve().parents[1] / "zodify" / "__init__.py"
MAX_LOGIC_LOC = 500


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


def test_logic_loc_budget_is_below_500_lines():
    logic_loc = compute_logic_loc(SOURCE_FILE)
    assert logic_loc <= MAX_LOGIC_LOC, (
        f"logic LOC budget exceeded: {logic_loc} > {MAX_LOGIC_LOC}"
    )
