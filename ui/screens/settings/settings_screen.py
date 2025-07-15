import os

from kivy.app import App  # Import App để có thể dùng App.get_running_app() làm fallback
from kivy.uix.screenmanager import Screen

# Bỏ dòng này đi: from models.settings_model import app_settings # KHÔNG import trực tiếp instance


class SettingsScreen(Screen):
    # Thêm một thuộc tính để giữ tham chiếu đến app_settings
    _app_settings_instance = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_list = []
        print(
            "DEBUG (SettingsScreen): Init SettingsScreen, font_list initialized:",
            self.font_list,
        )
        self.previous_screen = None  # tên màn hình trước để quay lại khi back

    # Thêm một phương thức setter để gán app_settings từ bên ngoài
    def set_app_settings(self, settings_instance):
        """
        Dùng để gán instance của AppSettings từ bên ngoài (ví dụ: từ lớp App chính).
        """
        self._app_settings_instance = settings_instance
        print(
            "DEBUG (SettingsScreen): AppSettings instance đã được gán cho SettingsScreen."
        )

    def get_app_settings(self):
        """
        Lấy instance của AppSettings.
        """
        if self._app_settings_instance is None:
            # Fallback nếu chưa được set, nhưng lý tưởng là nên được set qua set_app_settings
            print(
                "CẢNH BÁO (SettingsScreen): _app_settings_instance chưa được gán. Thử lấy từ App.get_running_app()."
            )
            if App.get_running_app():
                # Đảm bảo App.get_running_app().app_settings đã được gán trong App class
                self._app_settings_instance = App.get_running_app().app_settings
        return self._app_settings_instance

    def on_pre_enter(self):
        # Trước khi màn hình được hiển thị, tải các cài đặt và cập nhật UI
        print("DEBUG (SettingsScreen): on_pre_enter đã được gọi.")

        app_settings = self.get_app_settings()
        if app_settings is None:
            print(
                "LỖI (SettingsScreen): Không thể tải cài đặt UI vì app_settings chưa có."
            )
            return

        # Load danh sách font
        font_dir = "assets/fonts"
        if os.path.exists(font_dir):
            self.font_list = [
                f for f in os.listdir(font_dir) if f.lower().endswith((".ttf", ".otf"))
            ]
        else:
            self.font_list = []

        # Cập nhật Spinner fonts
        if "font_spinner" in self.ids:
            self.ids.font_spinner.values = self.font_list
            # Set giá trị mặc định hoặc giá trị đã lưu
            current_font_name = app_settings.get_setting(
                "font_name", "Roboto"
            )  # Lấy từ settings
            if current_font_name in self.font_list:
                self.ids.font_spinner.text = current_font_name
            elif (
                self.font_list
            ):  # Nếu font đã lưu không có, chọn font đầu tiên trong danh sách
                self.ids.font_spinner.text = self.font_list[0]
            else:  # Không có font nào
                self.ids.font_spinner.text = "Chọn font"

        settings = app_settings.get_all_settings()
        font_size_map = {10: "Nhỏ", 20: "Vừa", 30: "Lớn"}  # Cập nhật map kích thước

        if "font_size_spinner" in self.ids:
            # Lấy font_size hiện tại từ settings, sau đó ánh xạ sang chữ để hiển thị trên spinner
            self.ids.font_size_spinner.text = font_size_map.get(
                settings.get("font_size", 20), "Vừa"
            )

        if "color_spinner" in self.ids:
            self.ids.color_spinner.text = settings.get("text_color", "#000000")

        print("DEBUG (SettingsScreen): Cài đặt UI đã được cập nhật từ app_settings.")

    def save_settings(self):
        print("DEBUG (SettingsScreen): save_settings được gọi.")
        app_settings = self.get_app_settings()
        if app_settings is None:
            print(
                "LỖI (SettingsScreen): Không thể lưu cài đặt vì app_settings chưa có."
            )
            return

        font_size_map_reverse = {"Nhỏ": 10, "Vừa": 20, "Lớn": 30}

        # Đảm bảo bạn lấy text từ spinner
        font_size = font_size_map_reverse.get(self.ids.font_size_spinner.text, 20)
        text_color = self.ids.color_spinner.text
        font_name = self.ids.font_spinner.text

        app_settings.update(
            font_size=font_size, text_color=text_color, font_name=font_name
        )
        print("DEBUG (SettingsScreen): Đã lưu cài đặt.")

    def reset_settings(self):
        print("DEBUG (SettingsScreen): reset_settings được gọi.")
        app_settings = self.get_app_settings()
        if app_settings is None:
            print(
                "LỖI (SettingsScreen): Không thể reset cài đặt vì app_settings chưa có."
            )
            return

        # Lấy cài đặt mặc định từ app_settings instance
        defaults = app_settings._get_default_settings()
        app_settings.update(**defaults)
        print("DEBUG (SettingsScreen): Đã reset cài đặt về mặc định.")

        # Sau khi reset, cập nhật lại UI để hiển thị các giá trị mặc định mới
        self.on_pre_enter()

    # def go_back(self):
    #     # Quay lại màn hình trước
    #     if self.previous_screen:
    #         self.manager.current = self.previous_screen
