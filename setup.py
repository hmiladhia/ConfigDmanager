import os
import setuptools

from configDmanager import import_config, ConfigManager

conf = import_config('PackageConfigs.VersionConfig')

try:
    setuptools.setup(**conf)
finally:
    gversion, version = conf.version.rsplit('.', 1)
    version = int(version) + 1
    conf.version = f"{gversion}.{version}"
    ConfigManager.export_config_file(conf, 'VersionConfig', os.path.join(os.getcwd(), 'PackageConfigs'))
