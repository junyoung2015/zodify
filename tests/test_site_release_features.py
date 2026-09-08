"""Documentation release checks locate modular APIs without hiding broken imports."""
import importlib.util
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    'site_release_features',
    Path(__file__).resolve().parents[1] / 'site/scripts/verify-examples.py',
)
features = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(features)


def test_candidate_modular_capabilities():
    assert features.detected_features() == {
        'compile': False, 'reports': False, 'validate_json': True,
        'json_schema_export': True, 'load_env': True, 'canonical_details': True,
    }


def test_missing_old_release_module_is_absent(monkeypatch):
    def missing(name):
        raise ModuleNotFoundError(name=name)
    monkeypatch.setattr(features.importlib, 'import_module', missing)
    assert not features.module_has_attribute('zodify.json_io', 'validate_json')


@pytest.mark.parametrize('error', [ModuleNotFoundError(name='unexpected_dependency'), ImportError('broken API')])
def test_internal_import_failure_propagates(monkeypatch, error):
    def broken(name):
        raise error
    monkeypatch.setattr(features.importlib, 'import_module', broken)
    with pytest.raises(type(error)) as caught:
        features.module_has_attribute('zodify.json_io', 'validate_json')
    assert caught.value is error
