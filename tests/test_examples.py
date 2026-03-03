"""Smoke tests for runnable examples and API coverage assertions."""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest
import zodify

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"
REQUIRED_EXAMPLES = [
    "basic_validation.py",
    "nested_schemas.py",
    "custom_validators.py",
    "union_types.py",
    "env_config.py",
    "structured_errors.py",
]
REQUIRED_RUNTIME_SYMBOLS = {"validate", "env", "Optional", "ValidationError"}


def discover_optional_examples() -> list[Path]:
    if not EXAMPLES_DIR.exists():
        return []
    required = set(REQUIRED_EXAMPLES)
    return sorted(
        path
        for path in EXAMPLES_DIR.glob("*.py")
        if not path.name.startswith("_") and path.name not in required
    )


def discover_runnable_examples() -> list[Path]:
    if not EXAMPLES_DIR.exists():
        return []
    required_paths = [EXAMPLES_DIR / name for name in REQUIRED_EXAMPLES]
    return required_paths + discover_optional_examples()


def _normalize_output(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(line.rstrip() for line in normalized.split("\n")).strip()


def _extract_expected_output(content: str, filename: str) -> str:
    marker = "# Expected output:"
    idx = content.find(marker)
    assert idx != -1, f"{filename} must include a '# Expected output:' block"
    lines = content[idx:].splitlines()[1:]
    extracted: list[str] = []
    for line in lines:
        if line == "#":
            extracted.append("")
            continue
        if line.startswith("# "):
            extracted.append(line[2:])
            continue
        break
    return _normalize_output("\n".join(extracted))


def _collect_zodify_imports(tree: ast.AST) -> tuple[set[str], set[str]]:
    """Return canonical imported symbols and local bound names from zodify imports."""
    canonical: set[str] = set()
    local_bound: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "zodify":
            for alias in node.names:
                canonical.add(alias.name)
                local_bound.add(alias.asname or alias.name)
    return canonical, local_bound


def _collect_defined_names(tree: ast.AST) -> set[str]:
    defined: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defined.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    defined.add(target.id)
    return defined


def test_required_examples_present() -> None:
    assert EXAMPLES_DIR.exists(), "examples/ directory missing"
    discovered = {path.name for path in EXAMPLES_DIR.glob("*.py")}
    assert discovered, "No examples found in examples/"
    missing = set(REQUIRED_EXAMPLES) - discovered
    assert not missing, f"Missing required example scripts: {sorted(missing)}"


@pytest.mark.parametrize("example", discover_runnable_examples(), ids=lambda p: p.stem)
def test_example_runs_successfully(example: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(example)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, (
        f"{example.name} failed with exit code {result.returncode}:\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )


@pytest.mark.parametrize("example", discover_runnable_examples(), ids=lambda p: p.stem)
def test_example_has_expected_output_block(example: Path) -> None:
    content = example.read_text(encoding="utf-8")
    _extract_expected_output(content, example.name)


@pytest.mark.parametrize("example", discover_runnable_examples(), ids=lambda p: p.stem)
def test_expected_output_matches_stdout(example: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(example)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"{example.name} failed; cannot validate expected output"
    content = example.read_text(encoding="utf-8")
    expected = _extract_expected_output(content, example.name)
    actual = _normalize_output(result.stdout)
    assert actual == expected, (
        f"{example.name} expected output mismatch:\n"
        f"expected:\n{expected}\n\nactual:\n{actual}"
    )


def test_examples_cover_public_api() -> None:
    calls: set[str] = set()
    names: set[str] = set()
    imported_canonical: set[str] = set()
    imported_local: set[str] = set()
    local_definitions: set[str] = set()

    for path in discover_runnable_examples():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        canonical, local = _collect_zodify_imports(tree)
        imported_canonical.update(canonical)
        imported_local.update(local)
        local_definitions.update(_collect_defined_names(tree))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                calls.add(node.func.id)
            if isinstance(node, ast.Name):
                names.add(node.id)

    missing_imports = REQUIRED_RUNTIME_SYMBOLS - imported_canonical
    assert not missing_imports, (
        "Required runtime symbols must be imported from zodify at least once: "
        f"missing {sorted(missing_imports)}"
    )

    assert "validate" in calls and "validate" in imported_local
    assert "env" in calls and "env" in imported_local
    assert "Optional" in names and "Optional" in imported_local
    assert "ValidationError" in names and "ValidationError" in imported_local

    shadowed = REQUIRED_RUNTIME_SYMBOLS & local_definitions
    assert not shadowed, (
        "Runtime symbols must not be locally redefined in examples: "
        f"{sorted(shadowed)}"
    )


def test_public_api_export_parity() -> None:
    assert "__version__" in zodify.__all__
