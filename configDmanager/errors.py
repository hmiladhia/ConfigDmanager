
class Error(Exception):
    pass


class ConfigError(Error):
    pass


class ReinterpretationError(ConfigError):
    def __init__(self, attr, value, message, type_=None):
        self.message = f"Param ({attr}: {value}) reinterpretation failed: {message}"
        self.type_ = type_

    def __str__(self):
        return self.message