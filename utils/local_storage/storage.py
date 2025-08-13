import pickle
import os

default_settings = {
    "turn_indicator": True,
    "movement_indicators": True,
    "in_game_highlighting": True,
    "drag_drop": True,
}

class SettingsFileManager:
    def __init__(self, filename='lsf-001.store'):
        self.filename = filename
        self.settings = self._load_settings()
    def _load_settings(self):
        """Load settings from the file or use default settings if the file does not exist."""
        if not os.path.exists(self.filename):
            self._store_data(default_settings)
            return default_settings
        return self._retrieve_data()

    def _store_data(self, data):
        """Store data to a file using pickle."""
        with open(self.filename, 'wb') as file:
            pickle.dump(data, file)

    def _retrieve_data(self):
        """Retrieve data from a file using pickle. Return an empty dictionary if the file does not exist."""
        try:
            with open(self.filename, 'rb') as file:
                data = pickle.load(file)
            return data
        except FileNotFoundError:
            return {}

    def get_setting(self, atrb):
        """Retrieve a setting attribute. Falls back to default if missing."""
        try:
            if atrb in self.settings:
                return self.settings.get(atrb)
            # Fallback to default if not present in persisted settings
            return default_settings.get(atrb, None)
        except AttributeError:
            return default_settings.get(atrb, None)

    def save_setting(self, atrb, value):
        """Update a setting attribute and save it to the file."""
        self.settings[atrb] = value
        self._store_data(self.settings)


settings_file_manager = SettingsFileManager()