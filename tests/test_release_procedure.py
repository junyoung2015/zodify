"""Release integrity and retry boundaries without publishing or network access."""
import importlib.util
import io
import json
import tarfile
import zipfile
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location('local_release', Path(__file__).resolve().parents[1] / 'scripts/release.py')
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)


@pytest.fixture
def candidate(tmp_path):
    version = '0.8.0'
    raw = b'Name: zodify\nVersion: 0.8.0\nRequires-Python: >=3.10\n'
    wheel = tmp_path / f'zodify-{version}-py3-none-any.whl'
    with zipfile.ZipFile(wheel, 'w') as archive:
        archive.writestr('zodify/py.typed', '')
        archive.writestr(f'zodify-{version}.dist-info/METADATA', raw)
    sdist = tmp_path / f'zodify-{version}.tar.gz'
    with tarfile.open(sdist, 'w:gz') as archive:
        for name, data in [('PKG-INFO', raw), ('zodify/py.typed', b'')]:
            item = tarfile.TarInfo(f'zodify-{version}/{name}')
            item.size = len(data)
            archive.addfile(item, io.BytesIO(data))
    log = tmp_path / 'checks.log'
    log.write_text('checks passed\n')
    notes = tmp_path / 'RELEASE_NOTES.md'
    notes.write_text('Release notes\n')
    manifest = {'format': 1, 'package': 'zodify', 'version': version, 'commit': 'a' * 40,
                'artifacts': [release.record(wheel), release.record(sdist)],
                'checks': release.record(log), 'notes': release.record(notes)}
    (tmp_path / 'manifest.json').write_text(json.dumps(manifest))
    return tmp_path


def test_valid_candidate(candidate):
    assert release.inspect(candidate)['version'] == '0.8.0'


@pytest.mark.parametrize('target', ['zodify-0.8.0-py3-none-any.whl', 'checks.log', 'RELEASE_NOTES.md'])
def test_tampered_file_rejected(candidate, target):
    (candidate / target).write_bytes(b'tampered')
    with pytest.raises(ValueError, match='integrity'):
        release.inspect(candidate)


@pytest.mark.parametrize('change', ['version', 'partial', 'path'])
def test_malformed_manifest(candidate, change):
    path = candidate / 'manifest.json'
    manifest = json.loads(path.read_text())
    if change == 'version':
        manifest['version'] = '0.9.0'
    elif change == 'partial':
        manifest['artifacts'].pop()
    else:
        manifest['checks']['name'] = '../checks.log'
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        release.inspect(candidate)


def files_for(manifest):
    return [{'filename': a['name'], 'size': a['size'], 'digests': {'sha256': a['sha256']}}
            for a in manifest['artifacts']]


def test_remote_partial_and_mismatch_are_not_retryable(candidate):
    manifest = release.inspect(candidate)
    files = files_for(manifest)
    assert release.compare_remote(manifest, []) == 'absent'
    assert release.compare_remote(manifest, files) == 'complete'
    with pytest.raises(ValueError, match='partial'):
        release.compare_remote(manifest, files[:1])
    files[0]['digests']['sha256'] = '0' * 64
    with pytest.raises(ValueError, match='differs'):
        release.compare_remote(manifest, files)


def test_upload_requires_exact_approval_before_network(candidate, monkeypatch):
    def forbidden(*args):
        pytest.fail('must not access network without approval')
    monkeypatch.setattr(release, 'remote_files', forbidden)
    with pytest.raises(ValueError, match='decision required'):
        release.upload(candidate, 'yes')


def test_upload_partial_never_calls_twine(candidate, monkeypatch):
    manifest = release.inspect(candidate)
    monkeypatch.setattr(release, 'remote_files', lambda version: files_for(manifest)[:1])
    monkeypatch.setattr(release.subprocess, 'run', lambda *a, **kw: pytest.fail('must not upload partial release'))
    approval = f'publish-zodify-0.8.0-{release.digest(candidate / "manifest.json")}'
    with pytest.raises(ValueError, match='partial'):
        release.upload(candidate, approval)


def test_metadata_version_mismatch(candidate):
    with pytest.raises(ValueError, match='version mismatch'):
        release.metadata(candidate / 'zodify-0.8.0-py3-none-any.whl', '0.9.0')


@pytest.mark.parametrize('outcome', ['success', 'already_complete', 'failed_absent', 'failed_complete'])
def test_upload_outcomes(candidate, monkeypatch, outcome):
    from types import SimpleNamespace
    files = files_for(release.inspect(candidate))
    responses = iter([files] if outcome == 'already_complete' else
                     [[], files if outcome == 'failed_complete' else []])
    inspections = []
    uploads = []
    verifications = []

    def remote(version):
        inspections.append(version)
        return next(responses)

    def run(command, **kwargs):
        uploads.append(command)
        assert '--skip-existing' not in command
        return SimpleNamespace(returncode=1 if outcome.startswith('failed_') else 0)

    monkeypatch.setattr(release, 'remote_files', remote)
    monkeypatch.setattr(release.subprocess, 'run', run)
    monkeypatch.setattr(release, 'verify_published', lambda path: verifications.append(path))
    approval = f'publish-zodify-0.8.0-{release.digest(candidate / "manifest.json")}'
    if outcome == 'failed_absent':
        with pytest.raises(ValueError, match='upload failed'):
            release.upload(candidate, approval)
        assert not verifications
    else:
        release.upload(candidate, approval)
        assert verifications == [candidate]
    assert len(uploads) == (0 if outcome == 'already_complete' else 1)
    assert len(inspections) == (2 if outcome.startswith('failed_') else 1)
