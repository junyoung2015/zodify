"""Run every published example against the explicitly installed released wheel.
Run from any directory: /path/to/release-venv/bin/python -I site/scripts/verify-examples.py
"""
import importlib
import importlib.metadata
import zodify
import json
from pathlib import Path
import subprocess
import sys
import tempfile

def module_has_attribute(module_name, attribute):
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        if exc.name != module_name:
            raise
        return False
    return hasattr(module, attribute)


def detected_features():
    return {
        "compile": hasattr(zodify, "compile"),
        "reports": hasattr(zodify, "inspect_validation"),
        "validate_json": module_has_attribute("zodify.json_io", "validate_json"),
        "json_schema_export": module_has_attribute("zodify.json_schema", "export_json_schema"),
        "load_env": hasattr(zodify, "load_env"),
        "canonical_details": hasattr(zodify.ValidationError([]), "details"),
    }


def main():
    site = Path(__file__).resolve().parents[1]
    release = json.loads((site / "src/release.json").read_text())
    examples = json.loads((site / "src/examples.json").read_text())
    assert importlib.metadata.version("zodify") == release["version"], "Use the recorded released wheel, not the working tree"
    for feature, available in detected_features().items():
        assert available == release["features"][feature], feature
    for name, example in examples.items():
        assert example["releasedVersion"] == release["version"]
        with tempfile.TemporaryDirectory(prefix="zodify-docs-") as directory:
            file = Path(directory) / (name + ".py")
            file.write_text(example["code"])
            result = subprocess.run([sys.executable, "-I", str(file)], cwd=directory, check=True, capture_output=True, text=True)
            assert result.stdout.strip() == example["expected"], (name, result.stdout)
        print(name + ": verified against " + release["version"])


if __name__ == "__main__":
    main()
