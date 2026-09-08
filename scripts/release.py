#!/usr/bin/env python3
"""Retain, inspect and publish one immutable local release candidate."""
from __future__ import annotations

import argparse
import email
import hashlib
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path):
    return {"name": path.name, "size": path.stat().st_size, "sha256": digest(path)}


def metadata(path, version):
    if path.name.endswith('.whl'):
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            candidates = [n for n in names if n.endswith('.dist-info/METADATA')]
            if 'zodify/py.typed' not in names or len(candidates) != 1:
                raise ValueError('invalid wheel package contents')
            raw = archive.read(candidates[0])
    else:
        with tarfile.open(path, 'r:gz') as archive:
            names = archive.getnames()
            candidates = [n for n in names if n.count('/') == 1 and n.endswith('/PKG-INFO')]
            if f'zodify-{version}/zodify/py.typed' not in names or len(candidates) != 1:
                raise ValueError('invalid sdist package contents')
            stream = archive.extractfile(candidates[0])
            if stream is None:
                raise ValueError('missing sdist metadata')
            raw = stream.read()
    msg = email.message_from_bytes(raw)
    if msg['Name'] != 'zodify' or msg['Version'] != version:
        raise ValueError('artifact package name/version mismatch')
    # Optional development extras are allowed; unconditional dependencies are not.
    if any(not re.search(r';\s*extra\s*==\s*[\"\']dev[\"\']\s*$', dep)
           for dep in msg.get_all('Requires-Dist', [])):
        raise ValueError('artifact has a required runtime dependency')
    if msg['Requires-Python'] != '>=3.10':
        raise ValueError('unexpected supported Python constraint')


def inspect(directory):
    manifest = json.loads((directory / 'manifest.json').read_text())
    version = manifest.get('version', '')
    if (manifest.get('format') != 1 or manifest.get('package') != 'zodify'
            or not re.fullmatch(r'\d+\.\d+\.\d+(?:(?:a|b|rc)\d+)?', version)
            or not re.fullmatch(r'[0-9a-f]{40}', manifest.get('commit', ''))):
        raise ValueError('invalid release manifest')
    expected = {f'zodify-{version}-py3-none-any.whl', f'zodify-{version}.tar.gz'}
    artifacts = manifest.get('artifacts', [])
    if len(artifacts) != 2 or {a.get('name') for a in artifacts} != expected:
        raise ValueError('manifest must contain exactly the versioned wheel and sdist')
    for item in artifacts + [manifest.get('checks', {}), manifest.get('notes', {})]:
        name = item.get('name', '')
        if not name or Path(name).name != name:
            raise ValueError('invalid manifest path')
        path = directory / name
        if path.is_symlink() or not path.is_file() or record(path) != item:
            raise ValueError(f'release file integrity failed: {name}')
    for item in artifacts:
        metadata(directory / item['name'], version)
    return manifest


def remote_files(version):
    try:
        with urllib.request.urlopen(f'https://pypi.org/pypi/zodify/{version}/json', timeout=30) as response:
            return json.load(response)['urls']
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return []
        raise


def compare_remote(manifest, files):
    expected = {a['name']: a for a in manifest['artifacts']}
    if not files:
        return 'absent'
    if len(files) != 2 or {f['filename'] for f in files} != set(expected):
        raise ValueError('partial or unexpected PyPI artifacts; inspect manually before retrying')
    for item in files:
        local = expected[item['filename']]
        if item['digests']['sha256'] != local['sha256'] or item['size'] != local['size'] or item.get('yanked'):
            raise ValueError('published artifact differs from candidate or is yanked')
    return 'complete'


def verify_published(directory):
    manifest = inspect(directory)
    files = remote_files(manifest['version'])
    if compare_remote(manifest, files) != 'complete':
        raise ValueError('version is not published')
    for item in files:
        url = item['url']
        if not url.startswith('https://files.pythonhosted.org/'):
            raise ValueError('unexpected artifact download host')
        with urllib.request.urlopen(url, timeout=60) as response:
            data = response.read()
        if len(data) != item['size'] or hashlib.sha256(data).hexdigest() != item['digests']['sha256']:
            raise ValueError('downloaded artifact hash mismatch')
    (directory / 'published.json').write_text(json.dumps({
        'verified_at': datetime.now(timezone.utc).isoformat(),
        'manifest_sha256': digest(directory / 'manifest.json'),
        'artifacts': manifest['artifacts'],
    }, indent=2) + '\n')
    print('PyPI metadata and downloaded artifact hashes match the retained candidate.')


def upload(directory, approval):
    manifest = inspect(directory)
    required = f"publish-zodify-{manifest['version']}-{digest(directory / 'manifest.json')}"
    if approval != required:
        raise ValueError(f'explicit owner release decision required: --approval {required}')
    state = compare_remote(manifest, remote_files(manifest['version']))
    if state == 'complete':
        verify_published(directory)
        return
    # Fixed public PyPI endpoint; credentials are resolved by Twine/keyring.
    result = subprocess.run([sys.executable, '-m', 'twine', 'upload', '--non-interactive',
                             '--repository-url', 'https://upload.pypi.org/legacy/',
                             *[str(directory / a['name']) for a in manifest['artifacts']]],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if result.returncode:
        # Reinspect before any retry, including failed/uncertain uploads.
        state = compare_remote(manifest, remote_files(manifest['version']))
        if state != 'complete':
            raise ValueError('upload failed; check local credentials and inspect PyPI before retrying')
    verify_published(directory)


def clean_commit():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('release preparation requires a clean working tree')
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()


def prepare():
    commit = clean_commit()
    versions = []
    for name, pattern in [
        ('pyproject.toml', r'^version = "([^"]+)"'),
        ('zodify/__init__.py', r'^__version__(?::[^=]+)?\s*=\s*"([^"]+)"'),
        ('tests/test_zodify.py', r'assert __version__ == "([^"]+)"'),
    ]:
        match = re.search(pattern, (ROOT / name).read_text(), re.MULTILINE)
        if not match:
            raise ValueError(f'cannot read version: {name}')
        versions.append(match.group(1))
    if len(set(versions)) != 1:
        raise ValueError('source version triad mismatch')
    version = versions[0]
    directory = ROOT / '.release' / f'{version}-{commit[:12]}'
    directory.mkdir(parents=True, exist_ok=False)
    checks = [
        ['scripts/check_public_repo_policy.py'], ['-m', 'pytest', 'tests/'],
        ['-m', 'pytest', '--doctest-modules', 'zodify/'], ['-m', 'mypy'], ['-m', 'pyright'],
        ['-m', 'flake8', 'zodify/', 'tests/', '--select=E9,F63,F7,F82'],
    ]
    with (directory / 'checks.log').open('w') as log:
        for command in checks:
            print('Checking:', ' '.join(command), flush=True)
            log.write('COMMAND: ' + ' '.join(command) + '\n')
            log.flush()
            subprocess.run([sys.executable, *command], cwd=ROOT, stdout=log, stderr=log, check=True)
        if clean_commit() != commit:
            raise ValueError('source commit changed during checks')
        # Build only committed source, excluding stale/ignored local build inputs.
        with tempfile.TemporaryDirectory(prefix='zodify-release-') as temp:
            source = Path(temp)
            archive = source / 'source.tar'
            subprocess.run(['git', 'archive', '--output', str(archive), commit], cwd=ROOT, check=True)
            with tarfile.open(archive) as tf:
                tf.extractall(source)
            subprocess.run([sys.executable, '-m', 'build', '--sdist', '--wheel', '--outdir', str(directory)],
                           cwd=source, stdout=log, stderr=log, check=True)
            wheel = next(directory.glob('*.whl'))
            sdist = next(directory.glob('*.tar.gz'))
            rebuilt = source / 'sdist-wheel'
            subprocess.run([sys.executable, '-m', 'pip', 'wheel', '--no-deps',
                            '--wheel-dir', str(rebuilt), str(sdist)],
                           cwd=source, stdout=log, stderr=log, check=True)
            rebuilt_wheels = list(rebuilt.glob('*.whl'))
            if len(rebuilt_wheels) != 1:
                raise ValueError('sdist rebuild did not produce exactly one wheel')
            metadata(rebuilt_wheels[0], version)
            log.write('SDIST REBUILT WHEEL: ' + json.dumps(record(rebuilt_wheels[0])) + '\n')
            for label, installed_wheel in [('wheel', wheel), ('sdist', rebuilt_wheels[0])]:
                venv = source / f'installed-{label}'
                subprocess.run([sys.executable, '-m', 'venv', str(venv)], stdout=log, stderr=log, check=True)
                python = venv / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
                subprocess.run([str(python), '-I', '-m', 'pip', 'install', '--no-deps', str(installed_wheel)],
                               cwd=venv, stdout=log, stderr=log, check=True)
                for example in sorted((source / 'examples').glob('*.py')):
                    log.write(f'INSTALLED {label} EXAMPLE: {example.name}\n')
                    log.flush()
                    subprocess.run([str(python), '-I', str(example)], cwd=venv, stdout=log, stderr=log, check=True)
        artifacts = sorted([*directory.glob('*.whl'), *directory.glob('*.tar.gz')])
        subprocess.run([sys.executable, '-m', 'twine', 'check', *map(str, artifacts)],
                       cwd=ROOT, stdout=log, stderr=log, check=True)
    notes = directory / 'RELEASE_NOTES.md'
    subprocess.run(['bash', 'scripts/prepare_release_notes.sh', f'v{version}', str(notes)], cwd=ROOT, check=True)
    manifest = {'format': 1, 'package': 'zodify', 'version': version, 'commit': commit,
                'prepared_at': datetime.now(timezone.utc).isoformat(),
                'python': sys.version, 'artifacts': [record(p) for p in artifacts],
                'checks': record(directory / 'checks.log'), 'notes': record(notes)}
    (directory / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    inspect(directory)
    print(f'Retained candidate: {directory}')
    print(f'Manifest SHA-256: {digest(directory / "manifest.json")}')
    print('Review retained evidence and obtain the owner release decision before upload.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['prepare', 'verify', 'verify-published', 'upload'])
    parser.add_argument('directory', nargs='?', type=Path)
    parser.add_argument('--approval', default='')
    args = parser.parse_args()
    try:
        if args.operation == 'prepare':
            prepare()
        elif args.directory is None:
            parser.error('directory is required')
        elif args.operation == 'verify':
            inspect(args.directory)
            print('Retained candidate integrity verified.')
        elif args.operation == 'verify-published':
            verify_published(args.directory)
        else:
            upload(args.directory.resolve(), args.approval)
    except (ValueError, OSError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        # Do not echo subprocess output or credentials.
        print(f'Release operation failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
