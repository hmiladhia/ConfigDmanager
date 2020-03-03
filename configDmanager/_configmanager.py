import os
import json
import sys

from itertools import chain
from pathlib import Path

from configDmanager import Config
from configDmanager.errors import ConfigNotFoundError
from configDmanager.config_types import JsonType


class ConfigManager:
    supported_types = {'json': JsonType}
    default_export_type = 'json'
    @classmethod
    def import_config(cls, name, path=None, type_='json'):
        level = 0
        if name.startswith('.'):
            if not path:
                path = os.getcwd()
            for character in name:
                if character != '.':
                    break
                level += 1
        return cls.__config_import(name[level:], path, level, type_)

    @classmethod
    def export_config_file(cls, obj, config_name=None, path=None, type_=None, **kwargs):
        config_path = cls.__get_config_path(config_name if config_name else obj.__class__.__name__, path, type_)
        config_dict = obj.to_dict()
        config_dict['__name'] = config_name
        type_ = config_dict.get('__type', None) if type_ is None else type_
        with open(config_path, 'w') as config_file:
            cls.supported_types[type_ if type_ else cls.default_export_type].export_config(config_dict,
                                                                                           config_file, **kwargs)

    @classmethod
    def __load_config(cls, config_name, path, type_=None):
        config_dict = cls.__read_config_file(config_name, path, type_)
        parent_config = cls.__load_parent_config(config_dict, path, type_)
        return Config(config_dict, parent_config, config_name, path, type_)

    @classmethod
    def __read_config_file(cls, config_name, path, type_=None):
        config_path = cls.__get_config_path(config_name, path, type_)
        with open(config_path, 'r') as config_file:
            config_dict = cls.supported_types[type_].import_config(config_file)
        return config_dict

    @classmethod
    def __load_parent_config(cls, config_dict, path, type_=None):
        parent_name = config_dict.get('__parent', None)
        parent_path = config_dict.get('__parent_path', path)
        parent_type = config_dict.get('__parent_type', type_)
        return cls.import_config(parent_name, parent_path, parent_type) if parent_name else None

    @classmethod
    def __config_import(cls, name, path, level=0, type_=None):
        cls.__sanity_check(name, path, level)
        base, _, name_base = name.rpartition('.')
        base = base.replace('.', '/')
        for c_path in chain([path], sys.path):
            try:
                if c_path:
                    cls.__sanity_check(name, c_path, level)
                    c_path = Path(c_path)
                    c_path = (c_path.parent if level == 2 else c_path) / base
                    return cls.__load_config(name_base, c_path, type_)
            except FileNotFoundError:
                pass
        raise ConfigNotFoundError(name, path)

    @staticmethod
    def __sanity_check(name, path, level):
        """Verify arguments are "sane"."""
        if not isinstance(name, str):
            raise TypeError('configuration name must be str, not {}'.format(type(name)))
        if level < 0:
            raise ValueError('level must be >= 0')
        if level > 0:
            if not isinstance(path, str):
                raise TypeError('path not set to a string')
            elif not path:
                raise ImportError('attempted relative import with no known path')
        if level > 2:
            raise ValueError('Invalid Path: level must be <= 2')
        if not name and level == 0:
            raise ValueError('Empty configuration name')

    @staticmethod
    def __get_config_path(config_name, path, type_=None):
        return Path(path) / (config_name + f'.{type_}')
