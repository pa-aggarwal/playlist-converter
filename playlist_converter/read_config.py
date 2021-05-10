import configparser


class ConfigReader:
    """Read a config file using the configparser module."""

    def __init__(self, config_path: str):
        self.config = configparser.ConfigParser()
        with open(config_path, "r") as config_file:
            self.config.read_file(config_file)

    def file_setting(self, key: str) -> str:
        return self.config.get("FILE_INFO", key)

    def api_setting(self, key: str) -> str:
        return self.config.get("API", key)
