# main.py
import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
import os

# Import các màn hình và SettingsModel
from ui.screens.library_screen.library_screen import LibraryScreen
from ui.screens.reader_screen.reader_screen import ReaderScreen
from ui.screens.chapter_screen.chapter_screen import ChapterScreen
from ui.screens.settings.settings_screen import SettingsScreen
from models.settings_model import SettingsModel # Import SettingsModel
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup


class TextStoryReaderApp(App):
    def build(self):
        self.settings_model = SettingsModel() # Tạo instance của SettingsModel ngay khi App khởi động

        kv_files = self.load_kv_files('./ui')
        for kv_file in kv_files:
            try:
                Builder.load_file(kv_file) # Sử dụng load_file để tải từ đường dẫn đầy đủ
                print(f"Đã tải file KV: {kv_file}")
            except Exception as e:
                print(f"Lỗi khi tải file KV {kv_file}: {e}")

        sm = ScreenManager()
        # Không cần truyền settings_model trực tiếp qua constructor nếu App là global
        sm.add_widget(LibraryScreen(name='library_screen'))
        sm.add_widget(ReaderScreen(name='reader_screen'))
        sm.add_widget(ChapterScreen(name='chapter_screen'))
        sm.add_widget(SettingsScreen(name='settings_screen'))

        # đặt library_screen làm màn hình mặc định
        sm.current = 'library_screen'

        return sm

    def load_kv_files(self, directory):
        kv_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.kv'):
                    kv_files.append(os.path.join(root, file))
        return kv_files


    def open_file_chooser(self):
        print("Mở hộp thoại chọn file!")
        
        # Path mặc định: os.getcwd() (thư mục làm việc hiện tại)
        # Trên Android, có thể muốn bắt đầu từ /storage/emulated/0/Download hoặc /storage/emulated/0/Documents
        # Tuy nhiên, điều này yêu cầu quyền đọc bộ nhớ ngoài.
        # Một cách an toàn hơn là bắt đầu từ đường dẫn mà python-for-android cung cấp cho bộ nhớ ngoài
        # Nhưng nếu chỉ là ví dụ đơn giản, os.getcwd() tạm thời là được.
        
        file_chooser = FileChooserListView(path=os.getcwd()) 

        popup = Popup(title="Select File",
                    content=file_chooser,
                    size_hint=(0.9, 0.9))
        
        file_chooser.bind(on_submit=lambda instance, selection, touch: self.selected_file(selection, popup))
        file_chooser.bind(on_cancel=popup.dismiss)

        popup.open()

    def selected_file(self, selection, popup):
        if selection:
            print(f"Đã chọn file: {selection[0]}")
            # Đây là nơi bạn sẽ xử lý file đã chọn
            # Ví dụ: self.load_story_from_file(selection[0])
        popup.dismiss()


if __name__ == '__main__':
    TextStoryReaderApp().run()
