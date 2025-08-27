# chapter_screen.py
from kivy.app import App
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.uix.button import Button  # Hoặc OneLineListItem nếu dùng KivyMD
from kivy.uix.label import Label  # Để hiển thị thông báo
from kivy.uix.screenmanager import Screen

from textstoryreader.services.book_reader import BookReader
from textstoryreader.ui.utils import show_error_popup


class ChapterScreen(Screen):
    book = ObjectProperty()  # Thuộc tính để lưu trữ thông tin sách

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "chapter_list_container" in self.ids:
            self.chapter_list_container = self.ids.chapter_list_container
        else:
            print("DEBUG (ChapterScreen): Lỗi: Không tìm thấy 'chapter_list_container'. Kiểm tra file KV.")

    def set_book(self, book):
        """Gọi hàm này trước khi chuyển sang ChapterScreen."""
        self.book = book

    def display_chapters(self, chapter_data_list):
        self.chapter_list_container.clear_widgets()
        for indexchapter, chapter in enumerate(chapter_data_list):
            item = Button(
                text=chapter,
                size_hint_y=None,
                height=dp(48),
                valign="middle",
                halign="left",
                text_size=(dp(200), None),
                shorten=True,  # Kích hoạt cắt bớt văn bản
                shorten_from="right",  # Chọn vị trí cắt bớt (mặc định là 'right')
                ellipsis_options={"text": "..."},  # (Tùy chọn) Thêm dấu ba chấm (...)
            )
            item.bind(on_release=lambda x, index=indexchapter: self.on_chapter_selected(index))
            self.chapter_list_container.add_widget(item)
        print(f"DEBUG (ChapterScreen): Đã tải {len(chapter_data_list)} chương vào danh sách.")

    def display_no_chapter(self):
        self.chapter_list_container.clear_widgets()
        no_chapter_label = Label(
            text="Không có chương nào để hiển thị.",
            size_hint_y=None,
            height=dp(48),
            valign="middle",
            halign="center",
            text_size=(dp(200), None),
        )
        self.chapter_list_container.add_widget(no_chapter_label)
        print("DEBUG (ChapterScreen): Không có chương nào để hiển thị.")

    def update_chapterlist_view(self):
        self.book_reader = BookReader(self.book)
        if self.book_reader is None:
            print("ERROR (chapterlistscreen): BookReader instance is None. Cannot update chapter list view.")
            show_error_popup(
                "Lỗi Khởi Tạo",
                "Không thể cập nhật giao diện danh sách chapter vì BookReader không được khởi tạo.",
            )
            pass
        chapter_data_list = self.book_reader.get_chapter_list()
        if chapter_data_list:
            self.display_chapters(chapter_data_list)
        else:
            self.display_no_chapter()

    def on_chapter_selected(self, chapter_data):
        app = App.get_running_app()
        reader_screen = app.root.get_screen("reader_screen")

        reader_screen.jump_to_chapter(chapter_data)
        self.manager.current = "reader_screen"
