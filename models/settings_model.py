import json
import os

SETTINGS_FILE = 'settings.json'
DEFAULT_SETTINGS = {
    'font_size': 16,
    'theme': 'light',
    'last_read_position': {}  # Dictionary để lưu vị trí đọc cuối cùng cho mỗi sách
}

class SettingsModel:
    def __init__(self):
        self.settings = self._load_settings()

    def _load_settings(self):
        """Tải cài đặt từ file JSON hoặc trả về mặc định nếu file không tồn tại."""
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Lỗi khi tải cài đặt từ {SETTINGS_FILE}: {e}")
                return DEFAULT_SETTINGS
        else:
            return DEFAULT_SETTINGS

    def save_settings(self):
        """Lưu cài đặt hiện tại vào file JSON."""
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Lỗi khi lưu cài đặt vào {SETTINGS_FILE}: {e}")

    def get(self, key):
        """Lấy giá trị của một cài đặt."""
        return self.settings.get(key)

    def set(self, key, value):
        """Đặt giá trị cho một cài đặt và lưu."""
        self.settings[key] = value
        self.save_settings()

    def get_last_read_position(self, book_filename):
        """Lấy vị trí đọc cuối cùng cho một cuốn sách."""
        return self.settings['last_read_position'].get(book_filename, 0)

    def save_last_read_position(self, book_filename, position):
        """Lưu vị trí đọc cuối cùng cho một cuốn sách."""
        self.settings['last_read_position'][book_filename] = position
        self.save_settings()

    def get_font_size(self):
        """Lấy kích thước font chữ."""
        return self.get('font_size')

    def set_font_size(self, size):
        """Đặt kích thước font chữ."""
        self.set('font_size', size)

    def get_theme(self):
        """Lấy theme hiện tại."""
        return self.get('theme')

    def set_theme(self, theme):
        """Đặt theme."""
        self.set('theme', theme)