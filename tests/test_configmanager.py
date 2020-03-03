import pytest

from configDmanager import import_config, Config
from configDmanager.errors import ConfigNotFoundError


def test_import_config():
    assert type(import_config('configs.FstringConfig')) == Config


def test_import_error():
    with pytest.raises(ConfigNotFoundError) as context:
        import_config('FstringConfig')
    assert str(context.value) == 'FstringConfig Not Found'
