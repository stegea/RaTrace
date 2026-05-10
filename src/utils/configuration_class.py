import configparser
from pathlib import Path
import os

# Resolve the config file path relative to this script's location (src/utils/ -> src/config.ini)
SCRIPT_DIR = Path(__file__).parent  # src/utils/
SRC_DIR = SCRIPT_DIR.parent         # src/
CONFIG_FILE = SRC_DIR / 'config.ini'  # Absolute path to src/config.ini
PATH_BASE_DIR = SRC_DIR

class ConfigManagerClass:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManagerClass, cls).__new__(cls)
            cls._instance._config = configparser.ConfigParser()
            cls._instance.config_file = str(CONFIG_FILE)  # Use the resolved absolute path
            cls._instance.load_config()
        return cls._instance

    def load_config(self):
        if CONFIG_FILE.exists():
            self._config.read(str(CONFIG_FILE))
            print(f'Config file loaded: {CONFIG_FILE}')
        else:
            print(f'Config file does not exist: {CONFIG_FILE}')

    def get(self, section, option, fallback=None):
        return self._config.get(section, option, fallback=fallback)

    def getint(self, section, option, fallback=None):
        return self._config.getint(section, option, fallback=fallback)

    def getfloat(self, section, option, fallback=None):
        return self._config.getfloat(section, option, fallback=fallback)

    def getboolean(self, section, option, fallback=None):
        return self._config.getboolean(section, option, fallback=fallback)

    def set(self, section, key, value):
        if not self._config.has_section(section):
            self._config.add_section(section)
        self._config.set(section, key, str(value))
        self.save_config()

    def resolve_path(self, path):
        path = Path(path)
        if path.is_absolute():
            return str(path)
        return str((PATH_BASE_DIR / path).resolve())

    def relative_path(self, path):
        try:
            return os.path.normpath(os.path.relpath(path, PATH_BASE_DIR))
        except ValueError:
            return os.path.normpath(path)

    def save_config(self):
        with open(self.config_file, 'w') as f:
            self._config.write(f)


# Singleton instance
config = ConfigManagerClass()
