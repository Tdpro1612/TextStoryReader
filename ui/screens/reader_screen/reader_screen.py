# reader_screen.py
from kivy.uix.screenmanager import Screen
# from kivy.uix.boxlayout import BoxLayout # Có thể không cần import nếu chỉ dùng KV
# from kivy.uix.label import Label         # Có thể không cần import nếu chỉ dùng KV
# from kivy.uix.scrollview import ScrollView # Có thể không cần import nếu chỉ dùng KV
from kivy.app import App
from kivy.metrics import dp # Cần thiết nếu bạn dùng dp() trong Python

class ReaderScreen(Screen):
    def __init__(self, **kwargs):
        # Đảm bảo gọi super().__init__ đầu tiên
        super().__init__(**kwargs)
        print(f"DEBUG (ReaderScreen): __init__ method called! Instance: {self}")
        print(f"DEBUG (ReaderScreen):    self.ids (in __init__): {self.ids}")

        # Lấy tham chiếu đến các widget từ self.ids
        if 'book_title_label' in self.ids:
            self.book_title_label = self.ids.book_title_label
            print("DEBUG (ReaderScreen): 'book_title_label' found in self.ids.")
        else:
            print("DEBUG (ReaderScreen): Lỗi: Không tìm thấy 'book_title_label' trong ids của ReaderScreen. Kiểm tra file KV.")

        # Lấy tham chiếu đến Label chứa nội dung sách (tôi đổi tên thành book_content_label để rõ ràng hơn)
        if 'book_content_label' in self.ids:
            self.book_content_label = self.ids.book_content_label
            print("DEBUG (ReaderScreen): 'book_content_label' found in self.ids.")
        else:
            print("DEBUG (ReaderScreen): Lỗi: Không tìm thấy 'book_content_label' trong ids của ReaderScreen. Kiểm tra file KV.")

        # Lấy tham chiếu đến ScrollView nếu muốn cuộn về đầu khi tải sách mới
        if 'book_content_scroll_view' in self.ids:
            self.book_content_scroll_view = self.ids.book_content_scroll_view
            print("DEBUG (ReaderScreen): 'book_content_scroll_view' found in self.ids.")
        else:
            print("DEBUG (ReaderScreen): Lỗi: Không tìm thấy 'book_content_scroll_view' trong ids của ReaderScreen. Kiểm tra file KV.")


    def load_book_content(self, book_name, content, book_filename):
        print(f"DEBUG (ReaderScreen): load_book_content called for: {book_name}")
        
        # Kiểm tra trước khi truy cập thuộc tính để tránh lỗi nếu ID không được tìm thấy
        if hasattr(self, 'book_title_label'):
            self.book_title_label.text = book_name
            print(f"DEBUG (ReaderScreen): Đã đặt tiêu đề sách: {book_name}")
        else:
            print("DEBUG (ReaderScreen): Lỗi: self.book_title_label không được khởi tạo. Không thể đặt tiêu đề.")

        # Kiểm tra trước khi truy cập thuộc tính
        if hasattr(self, 'book_content_label'): # Tôi đã đổi tên thành book_content_label
            self.book_content_label.text = content
            print(f"DEBUG (ReaderScreen): Đã đặt nội dung sách (một phần): {content[:100]}...")
            
            # Cuộn về đầu nội dung khi sách được tải
            if hasattr(self, 'book_content_scroll_view'):
                self.book_content_scroll_view.scroll_y = 1 # Đặt scroll về đầu (1.0 là trên cùng, 0.0 là dưới cùng)
                print("DEBUG (ReaderScreen): Đã cuộn nội dung về đầu.")
        else:
            print("DEBUG (ReaderScreen): Lỗi: self.book_content_label không được khởi tạo. Không thể đặt nội dung.")

        self.current_book_filename = book_filename

    def get_current_book_filename(self):
        """
        Trả về tên file của cuốn sách hiện đang được đọc.
        """
        # Đảm bảo current_book_filename đã được gán
        if hasattr(self, 'current_book_filename'):
            return self.current_book_filename
        return None # Trả về None nếu chưa có sách nào được đọc

    # Các hàm khác có thể cần:
    # - save_reading_position()
    # - load_reading_position()