import os
import setuptools

from configDmanager import import_config, ConfigManager

test = os.environ.get('Test', 'True') == 'True'

conf = import_config('PackageConfigs.VersionConfig')

try:
    setuptools.setup(**conf)
except Exception as e:
    print(e)
else:
    if not test:
        conf['__version.__patch'] += 1
        ConfigManager.export_config_file(conf, 'VersionConfig', os.path.join(os.getcwd(), 'PackageConfigs'))
