from kivy.clock import Clock
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.uix.screenmanager import Screen

from textstoryreader.services.book_reader import BookReader
from textstoryreader.ui.utils import hex_to_rgba, show_error_popup


class ReaderScreen(Screen):
    previous_screen: str = "reader_screen"
    font_name = StringProperty("Roboto")
    font_size = NumericProperty(24)
    text_color = ListProperty([0, 0, 0, 1])  # RGBA
    background_color = ListProperty([1, 1, 1, 1])  # RGBA
    line_spacing = NumericProperty(1.2)
    chapter_text = StringProperty("")
    # Lưu vị trí cuộn hiện tại để đồng bộ, KHÔNG bind ngược vào ScrollView.scroll_y trong KV
    scroll_y = NumericProperty(1.0)

    def __init__(self, settings, **kwargs):
        super().__init__(**kwargs)
        self.settings = settings
        self.book = None
        self.book_reader = None
        self._pending_scroll_bind = False

    def apply_settings(self):
        self.font_name = getattr(self.settings, "font_name", "Roboto")
        self.font_size = getattr(self.settings, "font_size", 24)
        self.text_color = hex_to_rgba(getattr(self.settings, "text_color", "#000000"))
        self.background_color = hex_to_rgba(getattr(self.settings, "background_color", "#FFFFFF"))
        # line_spacing giữ nguyên

    def set_book(self, book):
        """Gọi hàm này trước khi chuyển sang ReaderScreen."""
        self.book = book

    def on_pre_enter(self, *args):
        self.apply_settings()

    def update_reader_view(self, use_saved_scroll=True):
        self.book_reader = BookReader(self.book)
        if self.book_reader is None:
            print("ERROR (ReaderScreen): BookReader instance is None. Cannot update reader view.")
            show_error_popup(
                "Lỗi Khởi Tạo",
                "Không thể cập nhật giao diện đọc vì BookReader không được khởi tạo.",
            )
            return

        data = self.book_reader.get_content_chapter()
        target_scroll = data.get("last_position_in_chapter", 1.0) if use_saved_scroll else 1.0

        self.chapter_text = data.get("content", "")
        # Bind theo texture_size của Label để đảm bảo layout xong mới cuộn
        self._bind_scroll_after_layout(target_scroll)

    def _bind_scroll_after_layout(self, target_scroll):
        if self._pending_scroll_bind:
            return
        label = self.ids.get("chapter_content")
        if not label:
            # Thử lại ở frame sau nếu ids chưa sẵn sàng
            Clock.schedule_once(lambda dt: self._bind_scroll_after_layout(target_scroll), 0)
            return

        self._pending_scroll_bind = True

        def _setter(*_):
            self.scroll_to_position(target_scroll)
            try:
                label.unbind(texture_size=_setter)
            except Exception:
                pass
            self._pending_scroll_bind = False

        label.bind(texture_size=_setter)

    def scroll_to_position(self, scroll_pos):
        if not 0.0 <= scroll_pos <= 1.0:
            scroll_pos = 1.0
        sv = self.ids.get("scroll_view")
        if sv is None:
            Clock.schedule_once(lambda dt: self.scroll_to_position(scroll_pos), 0)
            return
        sv.scroll_y = scroll_pos
        self.scroll_y = sv.scroll_y
        print(f"Set scroll_y -> ScrollView.scroll_y={sv.scroll_y}")

    def go_back(self):
        self.save_history_reader()
        print("DEBUG: Navigating back to library_screen")
        self.manager.current = "library_screen"

    def back_chapter(self):
        if self.book_reader:
            self.book_reader.previous_chapter()
            self.update_reader_view(use_saved_scroll=False)
        else:
            show_error_popup("Lỗi", "Không thể quay lại chương trước.")

    def jump_to_chapter(self, chapter_order: int):
        if self.book_reader:
            self.book_reader.jump_to_chapter(chapter_order)
            self.update_reader_view(use_saved_scroll=False)
        else:
            show_error_popup("Lỗi", "Không thể nhảy đến chương.")

    def next_chapter(self):
        if self.book_reader:
            self.book_reader.next_chapter()
            self.update_reader_view(use_saved_scroll=False)
        else:
            show_error_popup("Lỗi", "Không thể chuyển sang chương tiếp theo.")

    def back_to_head(self):
        if self.book_reader:
            self.book_reader.jump_to_head()
            self.update_reader_view(use_saved_scroll=False)
        else:
            show_error_popup("Lỗi", "Không thể quay lại chương đầu.")

    def save_history_reader(self):
        if self.book_reader:
            self.book_reader.save_history_readingstate(self.scroll_y)
        else:
            print("ERROR (ReaderScreen): BookReader instance is None. Cannot save reading state.")
            show_error_popup(
                "Lỗi Lưu Trạng Thái",
                "Không thể lưu trạng thái đọc vì BookReader không được khởi tạo.",
            )
