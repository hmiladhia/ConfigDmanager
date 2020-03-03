import json

from abc import ABC


class TypeBase(ABC):
    @classmethod
    def import_config(cls, config_file, *args, **kwargs):
        pass

    @classmethod
    def export_config(cls, config_dict, file_path, *args, **kwargs):
        pass

    @classmethod
    def is_readable(cls, file_path):
        try:
            with open(file_path, 'r') as config_file:
                cls.import_config(config_file)
        except:
            return False
        return True


class JsonType(TypeBase):
    @classmethod
    def import_config(cls, config_file, *args, **kwargs):
        return json.load(config_file)

    @classmethod
    def export_config(cls, config_dict, file_path, *args, **kwargs):
        json.dump(config_dict, file_path, indent=kwargs.get('indent', 2))
