import pytest

import configDmanager


def test_config_d_manager_version():
    assert configDmanager.__version__ == configDmanager.import_config('PackageConfigs.VersionConfig').version
