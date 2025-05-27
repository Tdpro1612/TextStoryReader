# library_screen.py

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.app import App
import os
from kivy.lang import Builder
from kivy.metrics import dp # Đảm bảo dòng này có

# Import hàm đọc file txt từ parser_txt.py
from reader.parser_txt import read_book_txt

BOOK_FOLDER = 'books'
SUPPORTED_EXTENSIONS = ['.txt']


class LibraryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print(f"DEBUG (LibraryScreen): __init__ method called! Instance: {self}")
        # print(f"DEBUG (LibraryScreen):    self.id (in __init__): {self.id}") # <-- XÓA HOẶC COMMENT DÒNG NÀY
        print(f"DEBUG (LibraryScreen):    self.ids (in __init__): {self.ids}") # Sẽ là {} lúc này, nhưng không lỗi
         # DI CHUYỂN LOGIC ÁP DỤNG ID VÀ GỌI load_books() VÀO ĐÂY
        # VÌ self.ids ĐÃ CÓ DỮ LIỆU Ở ĐÂY RỒI
        if 'grid_layout_stories' in self.ids:
            self.grid_layout_stories = self.ids.grid_layout_stories
            print("DEBUG (LibraryScreen): 'grid_layout_stories' found in self.ids (in __init__). Calling load_books().")
            self.load_books() # GỌI load_books() NGAY TRONG __init__
        else:
            print("DEBUG (LibraryScreen): Lỗi: Không tìm thấy 'grid_layout_stories' trong ids của LibraryScreen (in __init__). Kiểm tra file KV.")
            # Điều này sẽ không xảy ra với kết quả debug hiện tại của bạn

    def load_books(self):
        book_list = []
        print(f"DEBUG (load_books): Đang trong load_books(). Đường dẫn thư mục sách: {BOOK_FOLDER}")
        if not os.path.exists(BOOK_FOLDER):
            os.makedirs(BOOK_FOLDER)
            print(f"DEBUG (load_books): Thư mục '{BOOK_FOLDER}' không tồn tại, đã tạo.")
        
        files_in_folder = os.listdir(BOOK_FOLDER)
        print(f"DEBUG (load_books): Các file được tìm thấy trong '{BOOK_FOLDER}': {files_in_folder}")

        for filename in files_in_folder:
            for ext in SUPPORTED_EXTENSIONS:
                if filename.endswith(ext):
                    book_name = os.path.splitext(filename)[0].replace('_', ' ').title()
                    book_list.append((book_name, filename))
                    print(f"DEBUG (load_books): Đã thêm sách vào danh sách: {book_name} ({filename})")
                    break
        
        print(f"DEBUG (load_books): Số lượng sách trong book_list: {len(book_list)}")

        if not hasattr(self, 'grid_layout_stories') or self.grid_layout_stories is None:
            print("DEBUG (load_books): LỖI NGHIÊM TRỌNG: self.grid_layout_stories không được khởi tạo trong load_books().")
            return

        self.grid_layout_stories.clear_widgets()
        print("DEBUG (load_books): Đã xóa các widget cũ trong grid_layout_stories.")

        if book_list:
            print("DEBUG (load_books): book_list có sách, bắt đầu thêm nút.")
            for book_name, filename in book_list:
                book_button = Button(
                    text=book_name,
                    size_hint_y=None,
                    height=dp(80)
                )
                print("DEBUG (load_books): đây là các tên book", book_name)
                book_button.book_filename = filename
                book_button.bind(on_press=self.open_book)
                self.grid_layout_stories.add_widget(book_button)
        else:
            print("DEBUG (load_books): book_list trống, hiển thị thông báo không có sách.")
            no_books_label = Label(
                text='Không có sách nào trong thư viện.',
                halign='center',
                valign='middle',
                font_size='18sp',
                color=(0.8, 0.2, 0.2, 1)
            )
            self.grid_layout_stories.add_widget(no_books_label)

    def open_book(self, instance):
        book_filename = instance.book_filename
        if book_filename.endswith('.txt'):
            content = read_book_txt(book_filename)
            book_name = os.path.splitext(book_filename)[0].replace('_', ' ').title()
            if content:
                print(f"DEBUG (open_book): Mở sách: {book_name} ({book_filename})")
                app = App.get_running_app()
                reader_screen = app.root.get_screen('reader_screen')
                reader_screen.load_book_content(book_name, content, book_filename)
                self.manager.current = 'reader_screen'
            else:
                print(f"DEBUG (open_book): Không thể đọc sách: {book_name} ({book_filename})")
        else:
            print(f"DEBUG (open_book): Định dạng file không được hỗ trợ: {book_filename}")

    def show_list_book(self):
        print("DEBUG (show_list_book): Gọi load_books() để làm mới danh sách.")
        self.load_books()