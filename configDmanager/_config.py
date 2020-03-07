import re

from os import environ
from collections.abc import MutableMapping

from configDmanager.errors import ReinterpretationError
from configDmanager._format import FileReader


class Config(MutableMapping):
    def __init__(self, config_dict: dict, parent: 'Config' = None, name: str = None, path=None, type_=None):
        self.__config_dict = dict()
        self.__parent = parent
        self.update(config_dict)

        # Meta data
        if name:
            self.set_value('__name', name)
        else:
            self.__name = None

        if type_:
            self.set_value('__type', type_)

        # Format Executors
        self.__file_reader = FileReader(path)

    def get_name(self):
        return self.__name

    def to_dict(self, private=True, include_parent=False):
        d = dict()
        if include_parent and self.__parent:
            d.update(self.__parent.to_dict(private, include_parent))
        d.update({
            self.__reverse_parse_key(k): self.__reverse_parse_value(v, private=private, include_parent=include_parent)
            for k, v in self.__config_dict.items() if (not k.startswith(self.__private_prefix) or private)})
        if private and self.__parent:
            d['__parent'] = self.__parent.get_name()
        return d

    def set_value(self, key, value):
        key = self.__parse_key(key)
        value = self.__parse_value(value, key)
        self.__config_dict[key] = value

    def format_string(self, text, regex=None):
        if regex is None:
            regex = r"(?<!\\)\${(.*?)}"
        matches = re.finditer(regex, text, re.MULTILINE | re.DOTALL)

        def get_value(match):
            try:
                value = self[match.group(1)]
            except KeyError:
                if match.group(1).startswith('os_environ') or match.group(1).startswith('read_file'):
                    value = match.group(0)[1:]
                else:
                    raise KeyError(match.group(1))
            return value

        text = re.sub(regex, get_value, text)
        return text

    def __repr__(self):
        return f"Config: {self.to_dict(private=True, include_parent=False)}"

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            self.__getattribute__(item)

    def __setattr__(self, key, value):
        if not key.startswith(self.__private_prefix):
            self.set_value(key, value)
        else:
            return super(Config, self).__setattr__(key, value)

    def __getitem__(self, k):
        if isinstance(k, dict):
            return Config({name: self[key] for key, name in k.items()})
        elif not (isinstance(k, str)) and hasattr(k, '__iter__'):
            return Config({key: self[key] for key in k})

        try:
            return self.__get_single_item(k)
        except KeyError as e:
            if self.__parent:
                try:
                    return self.__parent.__get_single_item(k)
                except KeyError:
                    pass
            raise KeyError(f'Could not find param {e} in {self.__name if self.__name else "config"}')

    def __get_single_item(self, sub_attributes):
        value = self.__get_raw_single_item(sub_attributes)
        if isinstance(value, str):
            value = self.__reinterpret_single_item(sub_attributes, value)
        return value

    def __reinterpret_single_item(self, sub_attributes, value):
        try:
            value = self.format_string(value)
        except RecursionError:
            raise ReinterpretationError(sub_attributes, value, 'Due to cycle - RecursionError', RecursionError)
        except KeyError as e:
            raise ReinterpretationError(sub_attributes, value,
                                        f"Could not find param {e} in FstringConfig", KeyError)
        except FileNotFoundError as e:
            raise ReinterpretationError(sub_attributes, value, e, FileNotFoundError)

        try:
            value = value.format(os_environ=environ, read_file=self.__file_reader)
        except KeyError as e:
            raise ReinterpretationError(sub_attributes, value,
                                        f'Could not find {e} in Environment variables', KeyError)
        except FileNotFoundError as e:
            raise ReinterpretationError(sub_attributes, value, e, FileNotFoundError)
        return value

    def __get_raw_single_item(self, sub_attributes):
        if isinstance(sub_attributes, str):
            sub_attributes = sub_attributes.split('.')
        if not sub_attributes:
            raise ValueError
        if len(sub_attributes) > 1:
            return self.__config_dict[sub_attributes[0]].__get_single_item(sub_attributes[1:])
        else:
            return self.__config_dict[sub_attributes[0]]

    def __setitem__(self, k, v) -> None:
        self.set_value(k, v)

    def __delitem__(self, v) -> None:
        del self.__config_dict[v]

    def __len__(self):
        return len(self.__config_dict)

    def __iter__(self):
        keys = {key for key in self.__config_dict if key and not key.startswith(self.__private_prefix)}
        if self.__parent:
            keys.update(self.__parent)
        return iter(keys)

    __private_prefix = f'_{__qualname__}'

    @classmethod
    def __parse_value(cls, value, name=None):
        if type(value) == dict:
            return Config(value, name=name)
        elif type(value) == Config:
            return value
        elif not (isinstance(value, str)) and hasattr(value, '__iter__'):
            return [cls.__parse_value(p) for p in value]
        return value

    @classmethod
    def __reverse_parse_value(cls, value, **args):
        if type(value) == Config:
            private = args.get('private', True)
            include_parent = args.get('include_parent', False)
            return value.to_dict(private=private, include_parent=include_parent)
        elif not (isinstance(value, str)) and hasattr(value, '__iter__'):
            return [cls.__reverse_parse_value(p) for p in value]
        return value

    @classmethod
    def __parse_key(cls, key):
        return f'{cls.__private_prefix}{key}' if key[:2] == '__' else key

    @classmethod
    def __reverse_parse_key(cls, key):
        n = len(cls.__private_prefix)
        return key[n:] if key.startswith(cls.__private_prefix) else key

