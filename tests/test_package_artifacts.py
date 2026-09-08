"""Artifact boundary tests for wheel/sdist example packaging policy."""

from __future__ import annotations

from dataclasses import dataclass
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

import pytest
import zodify

ROOT = Path(__file__).resolve().parent.parent
SOURCE_PACKAGE = ROOT / "zodify"
SCHEMA_MODULE = SOURCE_PACKAGE / "schema.py"
REQUIRED_EXAMPLES = {
    "basic_validation.py",
    "nested_schemas.py",
    "custom_validators.py",
    "union_types.py",
    "env_config.py",
    "json_schema_export.py",
    "structured_errors.py",
}


@dataclass(frozen=True)
class BuiltArtifacts:
    wheel_path: Path
    sdist_path: Path
    source_root: Path


def _export_candidate(tmp_path: Path) -> Path:
    """Build reviewed working files, never a stale HEAD or local build cache."""
    source_root = tmp_path / "candidate"
    source_root.mkdir()
    for name in ("LICENSE", "README.md", "API_CONTRACT.md", "pyproject.toml", "MANIFEST.in"):
        shutil.copy2(ROOT / name, source_root / name)
    for name in ("zodify", "examples"):
        shutil.copytree(ROOT / name, source_root / name,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    return source_root


def _build_artifacts(tmp_path: Path) -> BuiltArtifacts:
    source_root = _export_candidate(tmp_path)
    outdir = tmp_path / "dist"
    outdir.mkdir()

    result = subprocess.run(
        [sys.executable, "-m", "build", "--no-isolation", "--outdir", str(outdir)],
        cwd=source_root,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, (
        "build failed:\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    wheels = sorted(outdir.glob("*.whl"))
    sdists = sorted(outdir.glob("*.tar.gz"))
    assert wheels, "expected at least one wheel artifact"
    assert sdists, "expected at least one sdist artifact"
    return BuiltArtifacts(wheels[-1], sdists[-1], source_root)


def _venv_python(venv_dir: Path) -> Path:
    if sys.platform == "win32":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


@pytest.fixture
def built_artifacts(tmp_path: Path) -> BuiltArtifacts:
    return _build_artifacts(tmp_path)


def test_artifact_example_boundaries(built_artifacts: BuiltArtifacts) -> None:
    wheel_path = built_artifacts.wheel_path
    sdist_path = built_artifacts.sdist_path

    with zipfile.ZipFile(wheel_path) as wheel:
        wheel_names = set(wheel.namelist())
    assert not any(name.startswith("examples/") for name in wheel_names), (
        "wheel must not include examples/ runtime files"
    )

    with tarfile.open(sdist_path, mode="r:gz") as sdist:
        sdist_names = sdist.getnames()

    assert any(name.endswith("/API_CONTRACT.md") for name in sdist_names)

    assert not any("/tests/" in name or name.endswith("/tests") for name in sdist_names), (
        "sdist must not include repository test modules"
    )

    for filename in REQUIRED_EXAMPLES:
        assert any(name.endswith(f"examples/{filename}") for name in sdist_names), (
            f"sdist missing required example file: {filename}"
        )


def test_install_context_smoke_required_examples(
    built_artifacts: BuiltArtifacts, tmp_path: Path
) -> None:
    wheel_path = built_artifacts.wheel_path
    venv_dir = tmp_path / "venv"
    python = _venv_python(venv_dir)

    create_venv = subprocess.run(
        [sys.executable, "-m", "venv", str(venv_dir)],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert create_venv.returncode == 0, (
        "venv creation failed:\n"
        f"stdout:\n{create_venv.stdout}\n"
        f"stderr:\n{create_venv.stderr}"
    )

    install = subprocess.run(
        [str(python), "-m", "pip", "install", str(wheel_path)],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert install.returncode == 0, (
        "wheel install failed:\n"
        f"stdout:\n{install.stdout}\n"
        f"stderr:\n{install.stderr}"
    )

    for filename in sorted(REQUIRED_EXAMPLES):
        example_path = built_artifacts.source_root / "examples" / filename
        result = subprocess.run(
            [str(python), str(example_path)],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0, (
            f"install-context smoke failed for {filename}:\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )


def test_install_context_schema_public_surface_when_present(
    built_artifacts: BuiltArtifacts, tmp_path: Path
) -> None:
    schema_module = built_artifacts.source_root / "zodify" / "schema.py"
    if not schema_module.exists():
        return

    wheel_path = built_artifacts.wheel_path
    venv_dir = tmp_path / "schema-venv"
    python = _venv_python(venv_dir)

    create_venv = subprocess.run(
        [sys.executable, "-m", "venv", str(venv_dir)],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert create_venv.returncode == 0, (
        "venv creation failed:\n"
        f"stdout:\n{create_venv.stdout}\n"
        f"stderr:\n{create_venv.stderr}"
    )

    install = subprocess.run(
        [str(python), "-m", "pip", "install", str(wheel_path)],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert install.returncode == 0, (
        "wheel install failed:\n"
        f"stdout:\n{install.stdout}\n"
        f"stderr:\n{install.stderr}"
    )

    result = subprocess.run(
        [
            str(python),
            "-c",
            "import zodify; from zodify import Schema, Validator, to_json_schema, validate; "
            "assert hasattr(zodify, 'Schema'); "
            "assert hasattr(zodify, 'to_json_schema'); "
            "from importlib.metadata import metadata; "
            "assert zodify.__version__ == metadata('zodify')['Version']; "
            "assert not any('extra ==' not in req for req in (metadata('zodify').get_all('Requires-Dist') or [])); "
            "assert callable(validate); "
            "assert callable(to_json_schema); "
            "assert Validator is not None; "
            "assert Schema is not None; "
            "assert to_json_schema({'host': str})['properties']['host']['type'] == 'string'",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, (
        "install-context smoke failed for Schema / JSON Schema public surface:\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )


def test_public_schema_surface_requires_extracted_module_path() -> None:
    if not hasattr(zodify, "Schema"):
        return

    assert SCHEMA_MODULE.exists(), (
        "public Schema surface requires the approved extracted-module path at zodify/schema.py"
    )
