# Local package release procedure

Package publication is separate from building a candidate. Keep automation disabled
while its budget is unavailable. This procedure uses the existing PyPI project;
GitHub Pages continues to use locally built static artifacts.

## Prepare and review

Merge reviewed release preparation first. From a clean commit, with the development
environment installed, run:

```sh
.venv/bin/python scripts/release.py prepare
```

The equivalent shell entry point is `PATH="$PWD/.venv/bin:$PATH" ./scripts/release_preflight.sh`.
Preparation retains the exact wheel and source distribution under
`.release/<version>-<commit>/`, plus checks output, curated release notes and a JSON
manifest containing the source commit, Python version, file sizes and SHA-256 hashes.
It builds from committed source, checks metadata and typing markers, installs the
retained wheel without dependencies in an isolated environment, rebuilds a wheel from
the exact retained source distribution, and installs that rebuilt wheel in a separate
clean environment. Both installations run the same maintained examples; the rebuild
hash and output are retained in the checks log.
A failed preparation leaves its output for diagnosis; never upload that directory.
To rerun the same commit, move the failed directory aside first. Do not edit retained
files; a change requires a fresh candidate.

Review the complete checks log, supported Python matrix, diagnostics cost evidence,
compatibility notes and production website verification. Preparation checks the
invoking Python only; it does not establish the full supported-version matrix.
The owner makes the release decision against the manifest hash. Credentials must
remain in local Twine/keyring configuration; never put a token in these commands,
chat, logs or version control.

## Publish the retained files

Replace `CANDIDATE` with the retained directory. Verify it before requesting the
owner's release decision:

```sh
.venv/bin/python scripts/release.py verify CANDIDATE
.venv/bin/python scripts/release.py upload CANDIDATE --approval publish-zodify-VERSION-MANIFEST_SHA256
```

The approval value explicitly binds the decision to the version and reviewed
manifest. The upload command queries PyPI first and uses a fixed public PyPI
endpoint. An already complete matching release is verified without uploading.
A partial, different, unexpected or yanked artifact set stops publication for manual
inspection. Upload errors are rechecked against PyPI; there is no blind retry or
`--skip-existing`. Twine output is suppressed to avoid retaining credential details.
Missing authentication requires the owner to configure project-scoped credentials
locally. An uncertain network result requires another inspection before any retry.

## Verify publication, then announce

```sh
.venv/bin/python scripts/release.py verify-published CANDIDATE
```

This downloads both published files and checks their sizes and hashes against the
retained candidate, recording verification in `published.json`. Independently install
from PyPI into a new environment and run the released examples. Only then create the
matching `vVERSION` tag at the manifest commit and the final GitHub Release. Review
curated notes again: remove candidate/unreleased wording only after verification.
Update package availability in README and the website together, deploy the static
site, and check production routes, no-JavaScript behavior and examples.

Never overwrite a published version. For a defective publication, prepare a corrective
version and consider yanking the affected version through the project owner. Retain
previous artifacts and the known-good static website deployment for rollback.
