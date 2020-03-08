import re

from os import environ
from collections.abc import MutableMapping

from configDmanager.errors import ReinterpretationError, FormatExecutorError
from configDmanager._format import FileReader, EnvironReader


class Config(MutableMapping):
    __c_escape = '$'
    __c_regex = re.compile(r"(?<!\$)\${(.*?)}")
    __c_fe_regex = re.compile(r'\${(.*?)\[(.*?)\]}')

    def __init__(self, config_dict: dict, parent: 'Config' = None, name: str = None, path=None, type_=None):
        self.__config_dict = dict()
        self.__parent = parent
        self.update(config_dict)

        # Meta data
        if name:
            self.__set_single_item('__name', name, private=True)
        else:
            self.__name = None

        if type_:
            self.__set_single_item('__type', type_, private=True)

        # Format Executors
        self.__format_exec = dict(read_file=FileReader(path),
                                  os_environ=EnvironReader())

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

    def format_string(self, value, sub_attributes=None):
        try:
            value = self.__format_string(value)
        except RecursionError:
            raise ReinterpretationError(sub_attributes, value, 'Due to cycle - RecursionError', RecursionError)
        except KeyError as e:
            raise ReinterpretationError(sub_attributes, value,
                                        f"Could not find param {e} in FstringConfig", KeyError)
        except FormatExecutorError as e:
            raise ReinterpretationError(sub_attributes, value, e.msg, e.type_)

        return value

    def __set_value(self, key, value, private=True):
        new_key = self.__parse_key(key)
        if not private and key != new_key:
            raise ValueError('Trying to set private parameter')
        value = self.__parse_value(value)
        self.__config_dict[new_key] = value
        return value

    def __get_value(self, key, raw=False, private=True):
        key = self.__parse_key(key) if private else key
        value = self.__config_dict[key]
        if not raw and isinstance(value, str):
            value = self.format_string(value, key)
        return value

    def __get_single_item(self, key, private):
        try:
            return self.__get_single_local_item(key, private)
        except KeyError as e:
            if self.__parent:
                try:
                    return self.__parent.__get_single_local_item(key, private)
                except KeyError:
                    pass
            raise KeyError(f'Could not find param {e} in {self.__name if self.__name else "config"}')

    def __get_single_local_item(self, sub_attributes, private):
        sub_attributes = self.__get_sub_attributes_list(sub_attributes)
        if len(sub_attributes) == 1:
            return self.__get_value(sub_attributes[0], raw=False, private=private)
        else:
            conf = self.__get_value(sub_attributes[0], raw=True, private=private)
            return conf.__get_single_local_item(sub_attributes[1], private)

    def __set_single_item(self, sub_attributes, value, private):
        sub_attributes = self.__get_sub_attributes_list(sub_attributes)
        if len(sub_attributes) == 1:
            return self.__set_value(sub_attributes[0], value, private=private)
        else:
            try:
                conf = self.__get_value(sub_attributes[0], raw=True, private=private)
            except KeyError:
                conf = self.__set_value(sub_attributes[0], Config(dict()), private=private)
            conf.__set_single_item(sub_attributes[1], value, private)

    @staticmethod
    def __get_sub_attributes_list(sub_attributes):
        if isinstance(sub_attributes, str):
            sub_attributes = sub_attributes.split('.', 1)
        else:
            raise TypeError('Key should be of type str')
        return sub_attributes

    def __format_string(self, text):
        text = re.sub(self.__c_regex, self.__get_format_value, text)
        return self.__remove_escaped(text, self.__c_escape)

    def __get_format_value(self, match):
        try:
            return str(self[match.group(1)])
        except KeyError:
            if re.fullmatch(self.__c_fe_regex, match.group(0)):
                try:
                    return re.sub(self.__c_fe_regex,
                                  lambda m: str(self.__format_exec[m.group(1)][m.group(2)]), match.group(0))
                except KeyError:
                    pass
            raise KeyError(match.group(1))

    def __repr__(self):
        return f"Config: {self.to_dict(private=True, include_parent=False)}"

    def __str__(self):
        return str(self.to_dict(private=False, include_parent=False))

    def __getattr__(self, item):
        try:
            return self.__get_single_item(item, private=False)
        except KeyError:
            return self.__getattribute__(item)

    def __setattr__(self, key, value):
        if not key.startswith(self.__private_prefix):
            self.__set_single_item(key, value, private=True)
        else:
            return super(Config, self).__setattr__(key, value)

    def __getitem__(self, k):
        if isinstance(k, dict):
            return Config({name: self[key] for key, name in k.items()})
        elif not (isinstance(k, str)) and hasattr(k, '__iter__'):
            return Config({key: self[key] for key in k})

        return self.__get_single_item(k, private=True)

    def __setitem__(self, k, v) -> None:
        self.__set_single_item(k, v, private=True)

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

    @staticmethod
    def __remove_escaped(text, escape_char):
        is_escaped = False
        res = ""
        for c in text:
            if is_escaped:
                res += c
                is_escaped = False
            else:
                if c == escape_char:
                    is_escaped = True
                else:
                    res += c
        return res
