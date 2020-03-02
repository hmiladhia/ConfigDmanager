import setuptools

from configDmanager import import_config

conf = import_config('VersionConfig')

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(long_description=long_description, **conf)  # packages=setuptools.find_packages()