# main.py
import os

import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import (
    dp,
)  # Import dp nếu bạn dùng nó cho kích thước widget trong Python
from kivy.uix.boxlayout import BoxLayout  # Cần cho Popup
from kivy.uix.button import Button  # Cần cho Popup
from kivy.uix.label import Label  # Cần cho Popup
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager

from managers.book_manager import BookManager  # BookManager đã được import đúng cách
from managers.settings_model import AppSettings
from ui.screens.chapter_screen.chapter_screen import ChapterScreen

# Import các màn hình và SettingsModel
from ui.screens.library_screen.library_screen import LibraryScreen
from ui.screens.reader_screen.reader_screen import ReaderScreen
from ui.screens.settings.settings_screen import SettingsScreen


class ManagerContainer:
    def __init__(self):
        self.book_manager = None

        # self.settings_model = None # Có thể thêm các manager khác ở đây


class TextStoryReaderApp(App):
    # Thêm tham chiếu đến book_reader instance
    def build(self):
        # 1. Khởi tạo ManagerContainer
        self.managers = ManagerContainer()

        # 2. Khởi tạo BookManager và gán vào ManagerContainer
        self.managers.book_manager = BookManager()

        print(f"DEBUG (main.py): Kivy user_data_dir: {self.user_data_dir}")

        # Khởi tạo AppSettings
        self.app_settings = AppSettings()
        # self.managers.settings_model = self.app_settings # Nếu bạn muốn quản lý settings_model qua managers

        # Tải tất cả các file KV
        kv_files = self.load_kv_files("./ui")
        for kv_file in kv_files:
            try:
                Builder.load_file(
                    kv_file
                )  # Sử dụng load_file để tải từ đường dẫn đầy đủ
                print(f"Đã tải file KV: {kv_file}")
            except Exception as e:
                print(f"Lỗi khi tải file KV {kv_file}: {e}")

        sm = ScreenManager()

        # Lưu một tham chiếu đến LibraryScreen instance
        self.library_screen = LibraryScreen(name="library_screen")
        sm.add_widget(self.library_screen)

        # Thiết lập callbacks cho BookManager sau khi LibraryScreen đã được tạo và thêm vào SM
        # Điều này đảm bảo 'self.library_screen' đã có giá trị
        self.managers.book_manager.set_ui_callbacks(
            status_callback=self.update_status_label,
            update_book_list_callback=self.update_library_books_ui,
        )

        # Thêm các màn hình khác
        sm.add_widget(ReaderScreen(name="reader_screen"))
        sm.add_widget(ChapterScreen(name="chapter_screen"))
        sm.add_widget(SettingsScreen(name="settings_screen"))

        # Đặt library_screen làm màn hình mặc định
        sm.current = "library_screen"

        return sm

    def on_start(self):
        """
        Được gọi sau khi `build` hoàn tất và ứng dụng đang khởi chạy.
        Đây là nơi tốt để cập nhật UI lần đầu.
        """
        print("DEBUG (main.py): on_start called. Triggering initial UI update.")
        # Yêu cầu LibraryScreen cập nhật danh sách sách ban đầu
        if self.library_screen:
            self.library_screen.update_library_view()

        # (Tùy chọn) Nếu bạn có status_label ở nơi khác ngoài LibraryScreen, bạn có thể cập nhật nó ở đây
        # Ví dụ: app.root.ids.some_other_status_label.text = "Ứng dụng đã sẵn sàng!"

    def update_status_label(self, message):
        """
        Callback được BookManager gọi để cập nhật text của status_label trên LibraryScreen.
        """
        if (
            self.library_screen
            and hasattr(self.library_screen, "ids")
            and "status_label" in self.library_screen.ids
        ):
            self.library_screen.ids.status_label.text = message
            print(f"UI Status Updated: {message}")
        else:
            print(
                f"WARNING (main.py): Không tìm thấy status_label hoặc LibraryScreen chưa sẵn sàng để cập nhật: {message}"
            )
            self.show_simple_popup(
                "Cảnh báo UI", f"Không thể hiển thị trạng thái: {message}"
            )

    def update_library_books_ui(self):
        """
        Callback được BookManager gọi để yêu cầu LibraryScreen tải lại danh sách sách.
        """
        if self.library_screen:
            self.library_screen.update_library_view()
            print(
                "DEBUG (main.py): LibraryScreen đã được yêu cầu cập nhật danh sách sách."
            )
        else:
            print(
                "WARNING (main.py): LibraryScreen chưa sẵn sàng để cập nhật danh sách sách."
            )
            self.show_simple_popup(
                "Cảnh báo UI", "Màn hình thư viện chưa sẵn sàng để cập nhật sách."
            )

    def load_kv_files(self, directory):
        kv_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".kv"):
                    kv_files.append(os.path.join(root, file))
        return kv_files

    def show_simple_popup(self, title, message):
        """
        Hiển thị một popup đơn giản. Hữu ích cho các thông báo chung.
        """
        content = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        content.add_widget(
            Label(
                text=message,
                halign="center",
                valign="middle",
                text_size=(dp(250), None),
            )
        )

        close_button = Button(text="Đóng", size_hint=(1, None), height=dp(40))
        content.add_widget(close_button)

        popup = Popup(
            title=title,
            content=content,
            size_hint=(None, None),
            size=(dp(300), dp(200)),
            auto_dismiss=False,
        )

        close_button.bind(on_release=popup.dismiss)
        popup.open()


if __name__ == "__main__":
    TextStoryReaderApp().run()
