import configparser
import os

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.ini")

DEFAULTS = {
    "server": {"url": "http://localhost:8000"},
    "capture": {
        "select_hotkey": "ctrl+shift+c",
        "quit_hotkey": "ctrl+shift+q",
        "settings_hotkey": "ctrl+shift+s",
    },
    "output": {"lang": "ar", "game": ""},
    "audio": {"device": ""},
}


class Settings:
    """configparser wrapper that repairs missing sections/keys instead of
    crashing on save, and always has a value for every key `reader_client.py`
    and the settings GUI expect."""

    def __init__(self, path: str = SETTINGS_FILE):
        self.path = path
        self.config = configparser.ConfigParser()
        if os.path.exists(path):
            self.config.read(path, encoding="utf-8")
        self._apply_defaults()
        self.save()

    def _apply_defaults(self):
        for section, values in DEFAULTS.items():
            if not self.config.has_section(section):
                self.config.add_section(section)
            for key, value in values.items():
                if not self.config.has_option(section, key):
                    self.config.set(section, key, value)

    def get(self, section: str, key: str, fallback: str = "") -> str:
        return self.config.get(section, key, fallback=fallback)

    def set(self, section: str, key: str, value: str) -> None:
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))

    def save(self) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            self.config.write(f)


settings = Settings()
