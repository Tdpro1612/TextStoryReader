import math

from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.uix.screenmanager import Screen

from textstoryreader.services.book_reader import BookReader
from textstoryreader.ui.utils import hex_to_rgba, show_error_popup, text_slicer_backward, text_slicer_forward, token_text_string_to_word


class ReaderScreen(Screen):
    previous_screen: str = "reader_screen"
    font_name = StringProperty("Roboto")
    font_size = NumericProperty(24)
    text_color = ListProperty([0, 0, 0, 1])  # RGBA
    background_color = ListProperty([1, 1, 1, 1])  # RGBA
    line_spacing = NumericProperty(1.2)

    # Logic để quản lý các trang
    words_tokens = []  # Danh sách các từ đã được tách
    index_word_start = 0
    index_word_end = 0
    # Các giá trị cần có để show ra trong ui
    max_chars_to_show = NumericProperty(2000)  # số kí tự tối đa có thể show trong một trang
    page_content = StringProperty("")  # Nội dung của trang được show ra

    def __init__(self, settings, **kwargs):
        super().__init__(**kwargs)
        self.settings = settings
        self.book = None
        self.book_reader = None

    def apply_settings(self):
        self.font_name = getattr(self.settings, "font_name", "Roboto")
        self.font_size = getattr(self.settings, "font_size", 24)
        self.text_color = hex_to_rgba(getattr(self.settings, "text_color", "#000000"))
        self.background_color = hex_to_rgba(getattr(self.settings, "background_color", "#FFFFFF"))

    def set_book(self, book):
        self.book = book
        self.book_reader = BookReader(self.book)
        if self.book_reader is None:
            show_error_popup("Lỗi Khởi Tạo", "Không thể lấy dữ liệu lịch sử vì BookReader không được khởi tạo.")
            return

    def on_pre_enter(self, *args):
        self.apply_settings()

    def get_data_history(self):
        if self.book_reader is None:
            show_error_popup("Lỗi Khởi Tạo", "Không thể lấy dữ liệu lịch sử vì BookReader chưa được khởi tạo.")
            return
        data = self.book_reader.get_content_chapter()
        if data is None:
            show_error_popup("Lỗi Lấy Dữ Liệu", "Không thể lấy dữ liệu lịch sử đọc.")
            return
        self.index_word_start = data.get("index_word_start", 0)
        print(f"<Reader screen> Loaded reading state at word index {self.index_word_start}")
        full_text_in_chapter = data.get("content", "")
        self.words_tokens = token_text_string_to_word(full_text_in_chapter)

    def update_reader_view(self):
        self.get_data_history()
        print(f"<Reader screen> Total words tokens: {len(self.words_tokens)}")
        self.show_current_page()

    def show_current_page(self):
        if not self.words_tokens:
            self.page_content = ""
            self.index_word_start = 0
            self.index_word_end = 0
            print("<Reader screen> Words tokens is empty.")
            return
        line_number, per_char_in_line = self.calculate_optimal_page_size(self.font_size, self.line_spacing)
        if line_number <= 0 or per_char_in_line <= 0:
            self.page_content = ""
            print("<Reader screen> Cannot calculate page size (0 lines or 0 chars per line).")
            return
        self.page_content, self.index_word_end = text_slicer_forward(
            self.words_tokens, self.index_word_start, line_number, per_char_in_line
        )
        print(f"<Reader screen> Showing words from index {self.index_word_start} to {self.index_word_end}")

    def calculate_optimal_page_size(self, font_size_sp, line_spacing):
        """
        Tính toán số dòng và số ký tự trên mỗi dòng dựa trên kích thước màn hình
        và các giá trị cài đặt. Đã loại bỏ tham số density vì sẽ lấy từ Metrics.
        """
        # density = Metrics.density  Lấy density thực tế từ Kivy
        screen_width_pixels = Window.width
        screen_height_pixels = Window.height

        # Sử dụng dp() để chuyển đổi các giá trị dp sang pixels (đã bao gồm density)
        padding_horizontal_pixels = dp(15)
        padding_vertical_pixels = dp(20)

        # CHIỀU CAO CỦA THANH BUTTON
        # Bạn đã đặt chiều cao của BoxLayout chứa các nút là dp(60) trong file .kv
        button_bar_height_pixels = dp(60)

        # Tính toán kích thước hiển thị hiệu quả cho Label
        effective_width = screen_width_pixels - 2 * padding_horizontal_pixels
        effective_height = screen_height_pixels - 2 * padding_vertical_pixels - button_bar_height_pixels

        if effective_width <= 0 or effective_height <= 0:
            return 0, 0

        # Sử dụng sp() để chuyển đổi font size sp sang pixels
        # Dùng 0.6 là ước tính cho độ rộng trung bình của một ký tự
        line_height_pixels = sp(font_size_sp) * line_spacing
        avg_char_width_pixels = 0.65 * sp(font_size_sp)

        if line_height_pixels <= 0 or avg_char_width_pixels <= 0:
            return 0, 0

        max_lines = math.floor(effective_height / line_height_pixels)
        max_chars_per_line = math.floor(effective_width / avg_char_width_pixels)

        # Giữ lại logic trừ 1 dòng để tăng độ tin cậy của việc ngắt trang
        return max_lines - 2, max_chars_per_line

    def go_to_next_page(self):
        if self.index_word_end == len(self.words_tokens):
            result = self.book_reader.next_chapter()
            if result.get("content", "") == "":
                return
            return self.update_reader_view()
        self.index_word_start = self.index_word_end
        self.show_current_page()

    def go_to_previous_page(self):
        line_number, per_char_in_line = self.calculate_optimal_page_size(self.font_size, self.line_spacing)
        print(f"DEBUG (ReaderScreen): index start is {self.index_word_start}")
        if self.index_word_start == 0:
            result = self.book_reader.previous_chapter()
            # print(f"DEBUG (ReaderScreen): Previous chapter result: {result}")
            if result.get("content", "") == "":
                return
            self.get_data_history()
            self.index_word_end = len(self.words_tokens) - 1
            self.page_content, self.index_word_start = text_slicer_backward(
                self.words_tokens, self.index_word_end, line_number, per_char_in_line
            )
            return self.show_current_page()
        self.index_word_end = self.index_word_start
        new_index_end = self.index_word_start - 1
        if self.words_tokens[new_index_end] == "\n":
            new_index_end -= 1
        self.page_content, self.index_word_start = text_slicer_backward(self.words_tokens, new_index_end, line_number, per_char_in_line)
        return self.show_current_page()

    def go_back(self):
        self.save_history_reader()
        self.manager.current = "library_screen"

    def jump_to_chapter(self, chapter_order: int):
        if self.book_reader:
            print(f"Jumping to chapter {chapter_order}")
            self.book_reader.jump_to_chapter(chapter_order)
            self.update_reader_view()
        else:
            show_error_popup("Lỗi", "Không thể nhảy đến chương.")

    def back_to_head(self):
        if self.book_reader:
            self.book_reader.jump_to_head()
            self.update_reader_view()
        else:
            show_error_popup("Lỗi", "Không thể quay lại chương đầu.")

    def save_history_reader(self):
        if self.book_reader:
            self.book_reader.save_history_readingstate(index_word_start=self.index_word_start)
            print(f"<Reader screen> Saved reading state at word index {self.index_word_start}")
        else:
            show_error_popup("Lỗi Lưu Trạng Thái", "Không thể lưu trạng thái đọc vì BookReader không được khởi tạo.")
