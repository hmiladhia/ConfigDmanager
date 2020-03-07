
class Error(Exception):
    pass


class ConfigError(Error):
    pass


class ReinterpretationError(ConfigError):
    def __init__(self, attr, value, message, origin=None):
        if attr:
            self.message = f"Param ({attr}: {value}) reinterpretation failed: {message}"
        else:
            self.message = f"Reinterpretation of {value} failed: {message}"
        self.origin = origin

    def __str__(self):
        return self.message


class ConfigManagerError(Error):
    pass


class ConfigNotFoundError(ConfigManagerError):
    def __init__(self, config_name, config_path=None):
        self.message = f"{config_name} Not Found{' in ' + str(config_path) if config_path else ''}"

    def __str__(self):
        return self.message


class FormatExecutorError(Error):
    def __init__(self, msg, type_=None):
        self.msg = msg
        self.type_ = type_

    def __str__(self):
        return self.msg
