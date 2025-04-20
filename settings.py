import configparser
import os

SETTINGS_FILE = "settings.ini"

class Settings:
    def __init__(self):
        self.config = configparser.ConfigParser()
        if os.path.exists(SETTINGS_FILE):
            self.config.read(SETTINGS_FILE)
        else:
            self.config['TTS'] = {
                'provider': 'edge',
                'elevenlabs_api_key': '',
                'speed': '1.0',
                'volume': '100'
            }
            self.config['Hotkeys'] = {
                'select_area': 'ctrl+shift+c',
                'read_text': 'ctrl+shift+v',
                'toggle_lang': 'ctrl+shift+l',
                'show_dashboard': 'ctrl+shift+d'
            }
            self.save()

    def get(self, section, key, fallback=None):
        return self.config.get(section, key, fallback=fallback)

    def set(self, section, key, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))
        self.save()
        
    def save(self):
        with open(SETTINGS_FILE, 'w') as f:
            self.config.write(f)

settings = Settings()
