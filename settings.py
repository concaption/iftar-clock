import json
import os
import tempfile
from pathlib import Path

DEFAULT_SETTINGS = {
    # Font settings
    "font_family": "Arial",  # Use standard cross-platform fonts
    "font_size": 24,
    "font_color": "#ADD8E6",  # LightBlue
    
    # Background settings
    "background_color": "#000000",
    "opacity": 0.8,
    
    # Description settings
    "show_description": False,
    "description": "Time to Iftar",
    "description_font_color": "#FFFFFF",  # White
    "description_font_size": 12
}

class Settings:
    def __init__(self, **kwargs):
        self._settings = DEFAULT_SETTINGS.copy()
        self._settings.update(kwargs)
    
    def __getitem__(self, key):
        return self._settings.get(key)
    
    def __setitem__(self, key, value):
        self._settings[key] = value
    
    def to_dict(self):
        return self._settings.copy()

def get_settings_path():
    """Returns the path to the settings file"""
    return os.path.join(tempfile.gettempdir(), "iftar_clock_settings.json")

def load_settings():
    """Load settings from JSON file or return defaults if file doesn't exist"""
    settings_path = get_settings_path()
    
    if not os.path.exists(settings_path):
        return DEFAULT_SETTINGS.copy()
    
    try:
        with open(settings_path, 'r') as f:
            settings = json.load(f)
            # Merge with defaults to ensure all keys exist
            merged_settings = DEFAULT_SETTINGS.copy()
            merged_settings.update(settings)
            return merged_settings
    except Exception as e:
        print(f"Error loading settings: {e}")
        return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    """Save settings to JSON file"""
    settings_path = get_settings_path()
    
    try:
        with open(settings_path, 'w') as f:
            if isinstance(settings, Settings):
                json.dump(settings.to_dict(), f, indent=2)
            else:
                json.dump(settings, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False
