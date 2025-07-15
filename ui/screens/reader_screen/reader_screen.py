# Trong reader_screen.py

from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.metrics import dp
from kivy.properties import ObjectProperty, ListProperty, NumericProperty, StringProperty
from kivy.clock import Clock
from kivy.uix.label import Label
import re
from bs4 import BeautifulSoup
from kivy.utils import get_color_from_hex


class ReaderScreen(Screen):
    book_title = StringProperty("Tên Sách")
    
    # Dữ liệu sách theo form chuẩn: List[Dict[str, str]]
    book_data = ListProperty([]) 
    
    # Dữ liệu của chapter
    current_chapter_index = NumericProperty(0) # chỉ số của chapter đang đọc trong danh sách chapter
    chapter_pages = ListProperty([]) # tổng số trang của chapter sau khi chia
    current_reading_page_index = NumericProperty(0) # vị trí trang đang đọc được chia trong chapter

    # Dữ liệu để lưu trữ
    current_book_filename = StringProperty("")
    # reader_screen.load_book_content(book_filename, book_name, book_data, history_chapter_index=0, history_chapter_page=0)

    _app_settings_instance = None


    def __init__(self, **kwargs):
        super(ReaderScreen, self).__init__(**kwargs)
        print("DEBUG (ReaderScreen): ReaderScreen __init__ đã được gọi.")
        
        # Đặt các thuộc tính mặc định
        self.book_data = []
        self.chapter_pages = []
        self.current_chapter_index = 0
        self.current_reading_page_index = 0
        self.current_book_filename = ""

        self.load_and_apply_ui_settings() # Tải cài đặt ban đầu
        print("DEBUG (ReaderScreen): ReaderScreen __init__ đã được gọi.")

    def get_current_book_filename(self):
        return self.current_book_filename

    def on_enter(self, *args):
        print("DEBUG (ReaderScreen): on_enter đã được gọi. Đang tải và áp dụng cài đặt UI mới nhất.")
        self.load_and_apply_ui_settings() 

    def load_and_apply_ui_settings(self):
        """
        Tải các cài đặt UI từ app_settings và gán chúng vào 
        các thuộc tính Kivy của ReaderScreen để Kivy tự động cập nhật UI.
        """
        print("DEBUG (ReaderScreen): Hàm load_and_apply_ui_settings được gọi.")
        app = App.get_running_app()
        app_settings = app.app_settings
        # Lấy các giá trị từ app_settings (đối tượng AppSettings)
        self.current_font_name = app_settings.get_setting('font_name')
        self.current_font_size = app_settings.get_setting('font_size')
        self.current_text_color = get_color_from_hex(app_settings.get_setting('text_color'))
        self.current_bg_color = get_color_from_hex(app_settings.get_setting('background_color'))

        print(f"DEBUG (ReaderScreen): Cài đặt UI đã tải và áp dụng: "
              f"Font: {self.current_font_name}, Size: {self.current_font_size}, "
              f"Text Color: {self.current_text_color}, BG Color: {self.current_bg_color}")

    def load_book_content(self, book_filename, book_name, book_data, history_chapter_index=0, history_chapter_page=0):
        """
        Tải dữ liệu của một cuốn sách mới vào ReaderScreen.

        Args:
            book_filename (str): Tên file của cuốn sách (định danh duy nhất).
            book_name (str): Tên hiển thị của cuốn sách.
            book_data (list): Danh sách các chapter data: [{'index': X, 'title': 'Y', 'content': 'Z'}, ...].
            initial_chapter_index (int): Chỉ số chương ban đầu nếu không có lịch sử đọc.
            initial_chapter_page (int): Chỉ số trang ban đầu nếu không có lịch sử đọc.
        """
        print(f"DEBUG (ReaderScreen): load_book_content được gọi cho '{book_name}' ({book_filename})")

        # 1. Lưu trữ dữ liệu sách chính
        self.book_title = book_name
        self.current_book_filename = book_filename
        self.book_data = book_data

        # 2. Thiết lập vị trí đọc ban đầu (bỏ qua lịch sử theo yêu cầu)
        self.current_chapter_index = history_chapter_index
        self.current_reading_page_index = history_chapter_page
        print(f"DEBUG (ReaderScreen): Thiết lập vị trí mặc định: Chương {self.current_chapter_index}, Trang {self.current_reading_page_index}")
        
        # 3. Show content của chương
        Clock.schedule_once(self.repaginate_on_next_frame, 0)
        print("DEBUG (ReaderScreen): Đã lên lịch hiển thị nội dung chương.")

    # --- Các hàm xử lý kích thước (đã có từ trước) ---
    def _setup_size_binding(self, instance, value):
        # Giả sử Label hiển thị nội dung có id là 'book_content_label' (KHỚP VỚI KV)
        if 'book_content_label' in self.ids:
            self.ids.book_content_label.bind(size=self.on_content_display_label_size_changed)
            print("DEBUG (ReaderScreen): Đã thiết lập binding kích thước cho book_content_label.")
        else:
            print("CẢNH BÁO: Không tìm thấy ID 'book_content_label'. Không thể thiết lập binding kích thước.")

    def on_content_display_label_size_changed(self, instance, value):
        new_width = instance.size[0]
        if new_width != self._last_content_width:
            print(f"DEBUG (ReaderScreen): Chiều rộng book_content_label thay đổi: {new_width}. Đang lên lịch phân trang lại.")
            self._last_content_width = new_width
            Clock.schedule_once(self.repaginate_on_next_frame, 0)
        else:
            print(f"DEBUG (ReaderScreen): Kích thước không thay đổi đáng kể, không phân trang lại.")

    def repaginate_on_next_frame(self, dt):
        print("DEBUG (ReaderScreen): Gọi repaginate_current_chapter từ repaginate_on_next_frame.")
        self.repaginate_current_chapter()

    def repaginate_current_chapter(self):
        print(f"DEBUG (ReaderScreen): repaginate_current_chapter được gọi (chế độ 1 chương/1 trang).")
        
        if not self.book_data or not (0 <= self.current_chapter_index < len(self.book_data)):
            self.chapter_pages = []
            self.current_reading_page_index = 0
            print("CẢNH BÁO (ReaderScreen): Không có dữ liệu chương để phân trang (chế độ 1 chương/1 trang).")
            self.update_page_content()
            return

        current_chapter_content = self.book_data[self.current_chapter_index]['content']

        # Mỗi chương là một trang duy nhất
        self.chapter_pages = [current_chapter_content]
        self.current_reading_page_index = 0 
        
        print(f"DEBUG (ReaderScreen): Đã 'phân trang' chương {self.current_chapter_index} thành 1 trang.")
        
        self.update_page_content()

    def update_page_content(self):
        print(f"DEBUG (ReaderScreen): update_page_content được gọi. Chương: {self.current_chapter_index}, Trang: {self.current_reading_page_index}")
        
        # Kiểm tra Label hiển thị nội dung (ID KHỚP VỚI KV)
        if 'book_content_label' not in self.ids:
            print("LỖI (ReaderScreen): Không tìm thấy widget 'book_content_label' để cập nhật nội dung.")
            return

        content_label = self.ids.book_content_label
        
        if self.chapter_pages: 
            content = self.chapter_pages[0] 
            content_label.text = content
            print(f"DEBUG (ReaderScreen): Đã đặt nội dung sách (một phần): {content[:100]}...")
            
            # Cuộn về đầu nội dung khi sách được tải (cuộn ScrollView - ID KHỚP VỚI KV)
            if 'book_content_scroll_view' in self.ids: 
                scroll_view = self.ids.book_content_scroll_view
                scroll_view.scroll_y = 1 
                print("DEBUG (ReaderScreen): Đã cuộn nội dung về đầu ScrollView.")
            else:
                print("CẢNH BÁO (ReaderScreen): Không tìm thấy 'book_content_scroll_view' để cuộn.")

            # page_info_label đã bị loại bỏ khỏi KV của bạn, nên không cần code liên quan đến nó ở đây.
        else:
            content_label.text = "Không có nội dung sách để hiển thị."
            print("DEBUG (ReaderScreen): update_page_content: chapter_pages rỗng.")

    def jump_to_chapter(self, target_chapter_index):
        """
        Nhảy đến một chương cụ thể dựa trên chỉ số của nó.

        Args:
            target_chapter_index (int): Chỉ số (index) của chương muốn nhảy đến.
        """
        print(f"DEBUG (ReaderScreen): Yêu cầu nhảy đến chương có Index: {target_chapter_index}")

        # 1. Kiểm tra tính hợp lệ của chỉ số chương
        if not self.book_data:
            print("CẢNH BÁO (ReaderScreen): Không có dữ liệu sách để nhảy chương.")
            return

        if not (0 <= target_chapter_index < len(self.book_data)):
            print(f"CẢNH BÁO (ReaderScreen): Chỉ số chương {target_chapter_index} nằm ngoài giới hạn "
                  f"(0-{len(self.book_data)-1}). Không thể nhảy chương.")
            return
        
        # 2. Cập nhật chỉ số chương hiện tại
        self.current_chapter_index = target_chapter_index
        
        # 3. Reset chỉ số trang về 0 (vì chúng ta đang nhảy sang chương mới, bắt đầu từ đầu chương)
        self.current_reading_page_index = 0
        
        print(f"DEBUG (ReaderScreen): Đã đặt chương hiện tại thành {self.current_chapter_index}, trang {self.current_reading_page_index}.")

        # 4. Kích hoạt quá trình "phân trang" và hiển thị nội dung của chương mới
        # (Sẽ gọi repaginate_current_chapter và sau đó update_page_content)
        Clock.schedule_once(self.repaginate_on_next_frame, 0)
        print("DEBUG (ReaderScreen): Đã lên lịch hiển thị nội dung chương mới.")
