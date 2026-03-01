"""Verify built distribution artifacts contain required package data."""

from __future__ import annotations

import argparse
import sys
import tarfile
import zipfile
from pathlib import Path

EXPECTED_MARKER = "zodify/py.typed"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("dist_dir", type=Path)
    return parser.parse_args()


def check_wheel(path: Path) -> None:
    with zipfile.ZipFile(path) as zf:
        names = set(zf.namelist())
    if EXPECTED_MARKER not in names:
        raise ValueError(f"{path.name} is missing {EXPECTED_MARKER}")


def check_sdist(path: Path) -> None:
    with tarfile.open(path, mode="r:gz") as tf:
        names = tf.getnames()
    if not any(name.endswith(EXPECTED_MARKER) for name in names):
        raise ValueError(f"{path.name} is missing {EXPECTED_MARKER}")


def main() -> int:
    args = parse_args()
    dist_dir = args.dist_dir

    if not dist_dir.is_dir():
        print(f"dist directory not found: {dist_dir}", file=sys.stderr)
        return 2

    wheels = sorted(dist_dir.glob("*.whl"))
    sdists = sorted(dist_dir.glob("*.tar.gz"))

    if not wheels or not sdists:
        print("expected both wheel and sdist artifacts", file=sys.stderr)
        return 2

    for wheel in wheels:
        check_wheel(wheel)
        print(f"OK wheel: {wheel.name}")

    for sdist in sdists:
        check_sdist(sdist)
        print(f"OK sdist: {sdist.name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
