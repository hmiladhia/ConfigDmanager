import os

from configDmanager.errors import FormatExecutorError


class FormatExecutor:
    def __getitem__(self, item):
        return self._execute(item)

    def _execute(self, item):
        pass


class FileReader(FormatExecutor):
    def __init__(self, default_path):
        self.default_path = default_path

    def _execute(self, file_path):
        if os.path.isabs(file_path):
            return self.read_file(file_path)
        else:
            if self.default_path:
                path = os.path.join(self.default_path, file_path)
                if os.path.isfile(path):
                    return self.read_file(path)
            return self.read_file(file_path)

    @staticmethod
    def read_file(file_path):
        try:
            with open(file_path, 'r') as file:
                content = file.read()
        except FileNotFoundError as e:
            raise FormatExecutorError(e, FileNotFoundError)
        return content


class EnvironReader(FormatExecutor):
    def _execute(self, item):
        try:
            return os.environ[item]
        except KeyError as e:
            raise FormatExecutorError(f'Could not find {e} in Environment variables', KeyError)
