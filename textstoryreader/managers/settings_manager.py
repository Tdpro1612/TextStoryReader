import json
import os
from dataclasses import asdict

from kivy.app import App

from textstoryreader.models.settings import Settings


class SettingsManager:
    def __init__(self):
        dev_data_dir = os.path.join("textstoryreader", "data")
        if os.path.exists(dev_data_dir):
            self.settings_file = os.path.join(dev_data_dir, "settings.json")
            print(f"DEBUG: Using settings file from project data folder: {self.settings_file}")
        else:
            app_dir = App.get_running_app().user_data_dir
            if not os.path.exists(app_dir):
                os.makedirs(app_dir)
            self.settings_file = os.path.join(app_dir, "settings.json")
            print(f"DEBUG: Using settings file from user data folder: {self.settings_file}")

    def load_settings(self) -> Settings:
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return Settings(**data)
            except (json.JSONDecodeError, TypeError):
                print("WARNING: Corrupted settings file. Using default settings.")
        return Settings()

    def save_settings(self, settings_object: Settings):
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(asdict(settings_object), f, indent=4)
