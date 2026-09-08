"""Run every published example against the explicitly installed released wheel.
Run from any directory: /path/to/release-venv/bin/python -I site/scripts/verify-examples.py
"""
import importlib.metadata
import zodify
import json
from pathlib import Path
import subprocess
import sys
import tempfile

site = Path(__file__).resolve().parents[1]
release = json.loads((site / "src/release.json").read_text())
examples = json.loads((site / "src/examples.json").read_text())
assert importlib.metadata.version("zodify") == release["version"], "Use the recorded released wheel, not the working tree"
for feature, attribute in {"compile": "compile", "reports": "inspect_validation", "validate_json": "validate_json", "json_schema_export": "export_json_schema", "load_env": "load_env"}.items():
    assert hasattr(zodify, attribute) == release["features"][feature], attribute
assert hasattr(zodify.ValidationError([]), "details") == release["features"]["canonical_details"]
for name, example in examples.items():
    assert example["releasedVersion"] == release["version"]
    with tempfile.TemporaryDirectory(prefix="zodify-docs-") as directory:
        file = Path(directory) / (name + ".py")
        file.write_text(example["code"])
        result = subprocess.run([sys.executable, "-I", str(file)], cwd=directory, check=True, capture_output=True, text=True)
        assert result.stdout.strip() == example["expected"], (name, result.stdout)
    print(name + ": verified against " + release["version"])
