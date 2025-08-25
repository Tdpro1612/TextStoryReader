import os

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

from textstoryreader.managers.book_manager import BookManager
from textstoryreader.managers.settings_manager import SettingsManager
from textstoryreader.ui.screens.chapter_screen.chapter_screen import ChapterScreen

# Import các màn hình và SettingsModel
from textstoryreader.ui.screens.library_screen.library_screen import LibraryScreen
from textstoryreader.ui.screens.reader_screen.reader_screen import ReaderScreen
from textstoryreader.ui.screens.settings.settings_screen import SettingsScreen
from textstoryreader.ui.utils import show_error_popup


class ManagerContainer:
    def __init__(self):
        self.book_manager = None
        self.settings_manager = None
        self.history_manager = None


class TextStoryReaderApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.managers = ManagerContainer()
        self.managers.book_manager = BookManager()
        self.managers.settings_manager = SettingsManager()
        self.current_settings = self.managers.settings_manager.load_settings()

    def update_settings(self):
        # Tải đối tượng Settings mới
        new_settings = self.managers.settings_manager.load_settings()

        # Cập nhật từng thuộc tính một, điều này sẽ kích hoạt Kivy events
        self.current_settings.font_name = new_settings.font_name
        self.current_settings.font_size = new_settings.font_size
        self.current_settings.text_color = new_settings.text_color
        self.current_settings.background_color = new_settings.background_color

    def build(self):
        print(f"DEBUG (main.py): Kivy user_data_dir: {self.user_data_dir}")

        kv_files = self.load_kv_files("textstoryreader/ui")
        for kv_file in kv_files:
            try:
                Builder.load_file(kv_file)
                print(f"Đã tải file KV: {kv_file}")
            except FileNotFoundError:
                print(f"Lỗi: Không tìm thấy file KV '{kv_file}'.")
            except PermissionError:
                print(f"Lỗi: Không có quyền truy cập file KV '{kv_file}'.")
                show_error_popup("Lỗi Quyền Truy Cập", f"Không có quyền đọc file KV: {kv_file}")
            except Builder.BuilderException as e:  # Bắt lỗi cú pháp hoặc cấu trúc KV
                print(f"Lỗi cú pháp trong file KV '{kv_file}': {e}")
                show_error_popup("Lỗi KV", f"Lỗi cú pháp trong {kv_file}:\n{e}")
            except OSError as e:
                print(f"Lỗi hệ thống khi tải file KV '{kv_file}': {e}")
                show_error_popup("Lỗi Hệ Thống", f"Lỗi hệ thống khi tải {kv_file}:\n{e}")

        sm = ScreenManager()
        self.library_screen = LibraryScreen(name="library_screen")
        sm.add_widget(self.library_screen)

        # Thêm các màn hình khác
        self.reader_screen = ReaderScreen(name="reader_screen", settings=self.current_settings)
        sm.add_widget(self.reader_screen)

        sm.add_widget(ChapterScreen(name="chapter_screen"))
        sm.add_widget(SettingsScreen(name="settings_screen"))

        # Đặt library_screen làm màn hình mặc định
        sm.current = "library_screen"

        return sm

    def on_stop(self):
        """
        Phương thức này được gọi khi ứng dụng sắp bị đóng.
        Dùng để lưu trạng thái đọc hiện tại.
        """
        print("DEBUG: Ứng dụng sắp bị đóng. Tiến hành lưu trạng thái đọc.")
        # Lấy tham chiếu đến màn hình ReaderScreen
        reader_screen = self.root.get_screen("reader_screen")

        # Kiểm tra xem màn hình đó có đang hiển thị hay không và có đối tượng book_reader
        if self.root.current == "reader_screen" and reader_screen.book_reader:
            try:
                # Gọi hàm lưu trạng thái đọc từ ReaderScreen
                reader_screen.save_history_reader()
                print("DEBUG: Đã lưu trạng thái đọc thành công.")
            except Exception as e:
                print(f"ERROR: Lỗi khi lưu trạng thái đọc: {e}")

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
