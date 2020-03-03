import pytest

from configDmanager import import_config, Config
from configDmanager.errors import ConfigNotFoundError, ConfigManagerError


def test_import_config_json():
    assert type(import_config('configs.FstringConfig', type_='json')) == Config


def test_import_error():
    with pytest.raises(ConfigNotFoundError) as context:
        import_config('FstringConfig')
    assert str(context.value) == 'FstringConfig Not Found'


def test_import_error_unsupportedtype():
    with pytest.raises(ConfigManagerError) as context:
        import_config('configs.UnsupportedConfig')
    assert str(context.value) == 'Could not auto-detect type of Config: UnsupportedConfig'


def test_import_yaml():
    assert type(import_config('configs.YamlConfig', type_='yaml')) == Config


def test_automatic_import_detection_yaml():
    assert type(import_config('configs.YamlConfig')) == Config


def test_automatic_import_detection_json():
    assert type(import_config('configs.FstringConfig')) == Config
