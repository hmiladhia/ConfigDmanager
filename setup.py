import os
import setuptools

from configDmanager import import_config, ConfigManager

test = os.environ.get('Test', 'True')

conf_name = 'TestVersionConfig' if test == 'True' else 'VersionConfig'
conf = import_config(f'PackageConfigs.{conf_name}')

try:
    setuptools.setup(**conf)
finally:
    gversion, version = conf.version.rsplit('.', 1)
    version = int(version) + 1
    conf.version = f"{gversion}.{version}"
    ConfigManager.export_config_file(conf, conf_name, os.path.join(os.getcwd(), 'PackageConfigs'))
