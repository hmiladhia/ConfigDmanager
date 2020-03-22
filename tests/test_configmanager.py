import pytest

from configDmanager import import_config, export_config, Config
from configDmanager.errors import ConfigNotFoundError, ConfigManagerError


@pytest.mark.parametrize('config_name, type_', [
    ('configs.FstringConfig', 'json'),
    ('configs.YamlConfig', 'yaml'),
    ('configs.YamlConfig', 'YAML'),
])
def test_import_config(config_name, type_):
    assert type(import_config(config_name, type_=type_)) == Config


@pytest.mark.parametrize('config_name', [
    'configs.YamlConfig',
    'configs.FstringConfig'
])
def test_automatic_import_detection(config_name):
    assert type(import_config(config_name)) == Config


def test_import_error():
    with pytest.raises(ConfigNotFoundError) as context:
        import_config('FstringConfig')
    assert str(context.value) == 'FstringConfig Not Found'


def test_import_error_unsupportedtype():
    with pytest.raises(ConfigManagerError) as context:
        import_config('configs.UnsupportedConfig')
    assert str(context.value) == 'Could not auto-detect type of Config: UnsupportedConfig'


def test_export_config_manager():
    config = import_config('configs.ExportConfig')
    val = config['val']
    config.val += 1
    export_config(config, 'configs.ExportConfig')
    config = import_config('configs.ExportConfig')
    assert val + 1 == config.val
