import pytest

from configDmanager import import_config, Config
from configDmanager.errors import ConfigNotFoundError, ConfigManagerError


def test_import_config():
    assert type(import_config('configs.FstringConfig')) == Config


def test_import_error():
    with pytest.raises(ConfigNotFoundError) as context:
        import_config('FstringConfig')
    assert str(context.value) == 'FstringConfig Not Found'


def test_import_error_unsupportedtype():
    with pytest.raises(ConfigManagerError) as context:
        import_config('configs.UnsupportedConfig')
    assert str(context.value) == 'Could not auto-detect type of Config: UnsupportedConfig'
