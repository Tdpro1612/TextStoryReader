# chapter_screen.py
from kivy.app import App
from kivy.metrics import dp
from kivy.properties import ListProperty, StringProperty
from kivy.uix.button import Button  # Hoặc OneLineListItem nếu dùng KivyMD
from kivy.uix.label import Label  # Để hiển thị thông báo
from kivy.uix.screenmanager import Screen

# Nếu dùng KivyMD, bạn có thể cần import MDDialog và MDLabel thay thế Label


class ChapterScreen(Screen):
    chapters_display_list = ListProperty([])
    current_book_filename = StringProperty("")
    previous_screen_name = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Giả định bạn có một container trong KV để chứa danh sách chương
        if "chapter_list_container" in self.ids:
            self.chapter_list_container = self.ids.chapter_list_container
        else:
            print(
                "DEBUG (ChapterScreen): Lỗi: Không tìm thấy 'chapter_list_container'. Kiểm tra file KV."
            )

        # Thêm một Label để hiển thị thông báo khi không có chương
        # Bạn có thể định nghĩa nó trong KV với id, hoặc tạo động như này
        if "no_chapters_label" in self.ids:
            self.no_chapters_label = self.ids.no_chapters_label
        else:
            # Tạo động nếu không có trong KV. Điều chỉnh phù hợp với bố cục của bạn.
            self.no_chapters_label = Label(
                text="Sách này không có mục lục.",
                halign="center",
                valign="middle",
                font_size=dp(20),
                markup=True,  # Nếu bạn muốn dùng các tag markup
                size_hint_y=None,
                height=dp(100),
            )
            # Không add vào container ở đây, sẽ add khi cần

    def load_chapters(self, chapter_data_list):
        """
        Tải danh sách chương vào màn hình ChapterScreen.
        Kiểm tra nếu danh sách rỗng thì hiển thị thông báo.
        """
        self.chapters_display_list = chapter_data_list
        self.chapter_list_container.clear_widgets()  # Luôn xóa widgets cũ

        if not chapter_data_list:  # Nếu danh sách chương rỗng
            print("DEBUG (ChapterScreen): Không có chương nào. Hiển thị thông báo.")
            # Đảm bảo chỉ hiển thị 1 thông báo
            if self.no_chapters_label not in self.chapter_list_container.children:
                self.chapter_list_container.add_widget(self.no_chapters_label)
        else:
            # Nếu có chương, xóa thông báo (nếu có) và thêm các chương
            if self.no_chapters_label in self.chapter_list_container.children:
                self.chapter_list_container.remove_widget(self.no_chapters_label)

            for chapter in self.chapters_display_list:
                item = Button(  # Hoặc OneLineListItem nếu dùng KivyMD
                    text=chapter["title"],
                    size_hint_y=None,
                    height=dp(48),
                    valign="middle",
                    halign="left",
                    text_size=(self.chapter_list_container.width - dp(20), None),
                )
                item.bind(
                    on_release=lambda x, chap=chapter: self.on_chapter_selected(chap)
                )
                self.chapter_list_container.add_widget(item)
            print(
                f"DEBUG (ChapterScreen): Đã tải {len(self.chapters_display_list)} chương vào danh sách."
            )

    def set_current_book(self, filename):
        """Thiết lập tên file của cuốn sách hiện tại, được gọi từ ReaderScreen."""
        self.current_book_filename = filename
        print(f"DEBUG (ChapterScreen): Sách hiện tại cho mục lục: {filename}")

    def on_chapter_selected(self, chapter_data):
        """
        Xử lý khi một chương được chọn từ danh sách.
        Chuyển về ReaderScreen và yêu cầu cuộn đến chương.
        """
        # print(f"DEBUG (ChapterScreen): Đã chọn chương: {chapter_data['title']} ({chapter_data['link']})")

        app = App.get_running_app()
        reader_screen = app.root.get_screen("reader_screen")

        reader_screen.jump_to_chapter(chapter_data["index"])
        self.manager.current = "reader_screen"

    def _go_back(self):
        """
        Quay lại màn hình đã gọi Chapterscreen.
        """
        if self.manager and self.previous_screen_name:
            print(
                f"DEBUG (Chapterscreen): Quay lại màn hình: {self.previous_screen_name}"
            )
            self.manager.current = self.previous_screen_name
            # Reset previous_screen_name để tránh lỗi nếu Chapterscreen được gọi lại
            self.previous_screen_name = ""
        else:
            print(
                "CẢNH BÁO (Chapterscreen): Không tìm thấy màn hình trước đó. Quay về màn hình mặc định 'reader_screen'."
            )
            self.manager.current = "reader_screen"
