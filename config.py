# config.py
import json
import os


class config:
    def __init__(self):
        self.config_file = "game_config.json"
        self.music_enabled = True
        self.sound_effects_enabled = True
        self.music_volume = 0.3
        self.sound_effects_volume = 0.5
        self.dark_theme = False
        self.load()

    def load(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.music_enabled = data.get('music_enabled', True)
                    self.sound_effects_enabled = data.get('sound_effects_enabled', True)
                    self.music_volume = data.get('music_volume', 0.3)
                    self.sound_effects_volume = data.get('sound_effects_volume', 0.5)
                    self.dark_theme = data.get('dark_theme', False)
            except:
                self.save()

    def save(self):
        data = {
            'music_enabled': self.music_enabled,
            'sound_effects_enabled': self.sound_effects_enabled,
            'music_volume': self.music_volume,
            'sound_effects_volume': self.sound_effects_volume,
            'dark_theme': self.dark_theme
        }
        with open(self.config_file, 'w') as f:
            json.dump(data, f, indent=2)

    def update(self, music_enabled=None, sound_effects_enabled=None,
               music_volume=None, sound_effects_volume=None, dark_theme=None):
        if music_enabled is not None:
            self.music_enabled = music_enabled
        if sound_effects_enabled is not None:
            self.sound_effects_enabled = sound_effects_enabled
        if music_volume is not None:
            self.music_volume = max(0.0, min(1.0, music_volume))
        if sound_effects_volume is not None:
            self.sound_effects_volume = max(0.0, min(1.0, sound_effects_volume))
        if dark_theme is not None:
            self.dark_theme = dark_theme
        self.save()

# Создаем экземпляр класса config
config = config()