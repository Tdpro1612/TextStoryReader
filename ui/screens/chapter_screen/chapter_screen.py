from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.app import App

class ChapterScreen(Screen):
    def __init__(self, **kwargs):
        pass

    # def load_chapters(self):
    #     # Dữ liệu chương mẫu (bạn sẽ thay thế bằng logic thực tế)
    #     pass
    #     # chapters = [f"Chương {i+1}" for i in range(10)]
    #     # if chapters:
    #     #     for chapter_name in chapters:
    #     #         chapter_button = Button(text=chapter_name, size_hint_y=None, height=40)
    #     #         chapter_button.bind(on_press=self.open_chapter)
    #     #         self.grid_layout.add_widget(chapter_button)
    #     # else:
    #     #     no_chapters_label = Label(text='Không có chương nào.', halign='center', valign='middle')
    #     #     self.grid_layout.add_widget(no_chapters_label)

    # def open_chapter(self, instance):
    #     chapter_name = instance.text
    #     print(f"Mở chương: {chapter_name}")
    #     # Thêm logic để tải nội dung chương hoặc chuyển đến màn hình đọc với chương cụ thể
    #     app = App.get_running_app()
    #     # Ví dụ: Nếu bạn muốn thông báo cho reader_screen biết chương nào được chọn
    #     if app.root.has_screen('reader_screen'):
    #         reader_screen = app.root.get_screen('reader_screen')
    #         # Bạn có thể cần một hàm trong ReaderScreen để xử lý việc tải theo chương
    #         # reader_screen.load_chapter(chapter_name)
    #         pass
    #     self.manager.current = 'reader_screen' # Tạm thời chuyển về reader_screen