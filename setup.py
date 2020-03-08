import os
import setuptools

from configDmanager import import_config, ConfigManager

test = os.environ.get('Test', 'True')

conf_name = 'TestVersionConfig' if test == 'True' else 'VersionConfig'
conf = import_config(f'PackageConfigs.{conf_name}')

try:
    setuptools.setup(**conf)
finally:
    conf['__version.__patch'] += 1
    ConfigManager.export_config_file(conf, conf_name, os.path.join(os.getcwd(), 'PackageConfigs'))
