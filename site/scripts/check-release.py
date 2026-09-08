"""Read-only PyPI check for the reviewed site release manifest. No publication."""
import json
from pathlib import Path
from urllib.request import urlopen

manifest = json.loads((Path(__file__).resolve().parents[1] / "src/release.json").read_text())
with urlopen(manifest["source"], timeout=30) as response:
    published = json.load(response)
assert manifest["version"] == published["info"]["version"], "Review site content against the new PyPI release"
assert manifest["python"] == published["info"]["requires_python"]
wheels = [item for item in published["urls"] if item["filename"].endswith(".whl")]
assert any(item["digests"]["sha256"] == manifest["wheel_sha256"] for item in wheels)
print("PyPI confirms zodify " + manifest["version"] + ", Python " + manifest["python"] + ", and the recorded wheel hash")
