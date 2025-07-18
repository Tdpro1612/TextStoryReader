import os

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from managers.book_manager import BookManager
from managers.settings_model import AppSettings
from ui.popup_utils import show_simple_popup
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
    def build(self):  # pylint: disable=W0201
        # 1. Khởi tạo ManagerContainer
        self.managers = ManagerContainer()

        # 2. Khởi tạo BookManager và gán vào ManagerContainer
        self.managers.book_manager = BookManager()

        print(f"DEBUG (main.py): Kivy user_data_dir: {self.user_data_dir}")

        # Khởi tạo AppSettings
        self.app_settings = AppSettings()

        # Tải tất cả các file KV
        kv_files = self.load_kv_files("./ui")
        for kv_file in kv_files:
            try:
                Builder.load_file(kv_file)
                print(f"Đã tải file KV: {kv_file}")
            except FileNotFoundError:
                print(f"Lỗi: Không tìm thấy file KV '{kv_file}'.")
            except PermissionError:
                print(f"Lỗi: Không có quyền truy cập file KV '{kv_file}'.")
                show_simple_popup("Lỗi Quyền Truy Cập", f"Không có quyền đọc file KV: {kv_file}")
            except Builder.BuilderException as e:  # Bắt lỗi cú pháp hoặc cấu trúc KV
                print(f"Lỗi cú pháp trong file KV '{kv_file}': {e}")
                show_simple_popup("Lỗi KV", f"Lỗi cú pháp trong {kv_file}:\n{e}")
            except OSError as e:
                print(f"Lỗi hệ thống khi tải file KV '{kv_file}': {e}")
                show_simple_popup("Lỗi Hệ Thống", f"Lỗi hệ thống khi tải {kv_file}:\n{e}")

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

    def update_status_label(self, message):
        """
        Callback được BookManager gọi để cập nhật text của status_label trên LibraryScreen.
        """
        if self.library_screen and hasattr(self.library_screen, "ids") and "status_label" in self.library_screen.ids:
            self.library_screen.ids.status_label.text = message
            print(f"UI Status Updated: {message}")
        else:
            print(f"WARNING (main.py): Không tìm thấy status_label hoặc LibraryScreen chưa sẵn sàng để cập nhật: {message}")
            show_simple_popup("Cảnh báo UI", f"Không thể hiển thị trạng thái: {message}")

    def update_library_books_ui(self):
        """
        Callback được BookManager gọi để yêu cầu LibraryScreen tải lại danh sách sách.
        """
        if self.library_screen:
            self.library_screen.update_library_view()
            print("DEBUG (main.py): LibraryScreen đã được yêu cầu cập nhật danh sách sách.")
        else:
            print("WARNING (main.py): LibraryScreen chưa sẵn sàng để cập nhật danh sách sách.")
            show_simple_popup("Cảnh báo UI", "Màn hình thư viện chưa sẵn sàng để cập nhật sách.")

    @staticmethod
    def load_kv_files(directory):
        kv_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".kv"):
                    kv_files.append(os.path.join(root, file))
        return kv_files


if __name__ == "__main__":
    TextStoryReaderApp().run()
