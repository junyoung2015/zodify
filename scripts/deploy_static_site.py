#!/usr/bin/env python3
"""Publish a locally verified site to existing Pages without an Actions run.

Explicit operation: python scripts/deploy_static_site.py --deploy
Preserves the existing domain and uses a normal, non-forced gh-pages push.
"""

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(args, cwd=cwd, text=True).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deploy", action="store_true", required=True)
    parser.parse_args()
    if run("git", "status", "--porcelain"):
        raise SystemExit("Commit the verified candidate before deploying.")
    # Build after checking the source tree so deployment provenance matches HEAD.
    run("npm", "ci", cwd=ROOT / "site")
    run("npm", "run", "lint", cwd=ROOT / "site")
    run("npm", "run", "build", cwd=ROOT / "site")
    dist = ROOT / "site" / "dist"
    if (dist / "CNAME").read_text().strip() != "zodify.dev":
        raise SystemExit("Unexpected domain; refusing hosting changes.")
    repo = json.loads(run("gh", "repo", "view", "--json", "nameWithOwner"))["nameWithOwner"]
    settings = json.loads(run("gh", "api", f"repos/{repo}/pages"))
    if settings["cname"] != "zodify.dev":
        raise SystemExit("Existing Pages domain differs; review configuration.")
    actions = json.loads(run("gh", "api", f"repos/{repo}/actions/permissions"))
    if actions["enabled"]:
        raise SystemExit("This September deployment path requires Actions disabled.")
    source = run("git", "rev-parse", "HEAD")
    remote = run("git", "remote", "get-url", "origin")
    with tempfile.TemporaryDirectory(prefix="zodify-pages-") as directory:
        target = Path(directory)
        run("git", "init", "-b", "gh-pages", cwd=target)
        run("git", "remote", "add", "origin", remote, cwd=target)
        if run("git", "ls-remote", "--heads", "origin", "gh-pages", cwd=target):
            run("git", "fetch", "origin", "gh-pages", cwd=target)
            run("git", "checkout", "-B", "gh-pages", "FETCH_HEAD", cwd=target)
            run("git", "rm", "-r", "--ignore-unmatch", ".", cwd=target)
        shutil.copytree(dist, target, dirs_exist_ok=True)
        (target / ".nojekyll").touch()
        (target / "deployment.json").write_text(json.dumps({"source_commit": source}, indent=2) + "\n")
        run("git", "add", ".", cwd=target)
        run("git", "commit", "-m", f"chore(site): deploy static documentation from {source[:12]}", cwd=target)
        run("git", "push", "origin", "gh-pages", cwd=target)
        configuration = {"build_type": "legacy", "source": {"branch": "gh-pages", "path": "/"}}
        subprocess.run(["gh", "api", "--method", "PUT", f"repos/{repo}/pages", "--input", "-"],
                       input=json.dumps(configuration), text=True, check=True, cwd=ROOT)
        # A first switch from workflow to branch publishing can otherwise
        # continue serving the old artifact until Pages receives a publish request.
        run("gh", "api", "--method", "POST", f"repos/{repo}/pages/builds")
        print(json.dumps({"source_commit": source, "pages_commit": run("git", "rev-parse", "HEAD", cwd=target),
                          "previous_pages_settings": settings}, indent=2))


if __name__ == "__main__":
    main()
