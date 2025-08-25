# library_screen.py


from kivy.app import App
from kivy.metrics import dp
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

from textstoryreader.services.android_handle import my_android_handler
from textstoryreader.ui.utils import show_error_popup


class LibraryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print(f"DEBUG (LibraryScreen): __init__ method called! Instance: {self}")

    def on_enter(self, *args):
        app = App.get_running_app()
        if hasattr(app, "managers") and hasattr(app.managers, "book_manager"):
            self.book_manager_instance = app.managers.book_manager
            print("DEBUG (LibraryScreen): BookManager instance retrieved from App.managers.")
        else:
            print("ERROR (LibraryScreen): BookManager not found in App.managers. Make sure it's initialized in your App class.")
            show_error_popup(
                "Lỗi Khởi Tạo",
                "Không thể tìm thấy BookManager.\nVui lòng kiểm tra cấu hình ứng dụng.",
            )
            self.book_manager_instance = None
        self.update_library_view()

    def update_library_view(self):
        if self.book_manager_instance is None:
            print("ERROR (LibraryScreen): BookManager instance is None. Cannot update library view.")
            show_error_popup(
                "Lỗi Khởi Tạo",
                "Không thể cập nhật giao diện thư viện vì BookManager không được khởi tạo.",
            )
            return
        if "grid_layout_stories" in self.ids:
            self.grid_layout_stories = self.ids.grid_layout_stories
            print("DEBUG (LibraryScreen): 'grid_layout_stories' found in self.ids (in update_library_view).")

            # Truy cập book_manager thông qua App
            app = App.get_running_app()
            if hasattr(app, "managers") and hasattr(app.managers, "book_manager"):
                book_manager_instance = app.managers.book_manager
                print("DEBUG (LibraryScreen): BookManager instance retrieved from App.managers.")
            else:
                print("ERROR (LibraryScreen): BookManager not found in App.managers. Make sure it's initialized in your App class.")
                show_error_popup(
                    "Lỗi Khởi Tạo",
                    "Không thể tìm thấy BookManager.\nVui lòng kiểm tra cấu hình ứng dụng.",
                )
                return

            book_list = book_manager_instance.get_book_list()
            self.grid_layout_stories.clear_widgets()

            if book_list:
                print("DEBUG (LibraryScreen - display_library): book_list có sách, bắt đầu thêm nút.")

                for book in book_list:
                    print(f"check button thêm vào :{book}")
                    book_button = Button(text=book.book_title, size_hint_y=None, height=dp(80))
                    book_button.book_name = book.book_name
                    book_button.book_filename = book.book_title
                    book_button.file_path = book.file_path
                    book_button.bind(on_press=self.open_book)
                    self.grid_layout_stories.add_widget(book_button)
            else:
                print("DEBUG (LibraryScreen - display_library): book_list trống, hiển thị thông báo không có sách.")
                no_books_label = Label(
                    text="Không có sách nào trong thư viện.",
                    halign="center",
                    valign="middle",
                    text_size=(dp(300), None),
                )
                self.grid_layout_stories.add_widget(no_books_label)
        else:
            print("ERROR (LibraryScreen): 'grid_layout_stories' not found in self.ids (in update_library_view). Check KV file.")
            show_error_popup(
                "Lỗi Giao Diện",
                "Không thể tìm thấy thành phần giao diện 'grid_layout_stories'.\nVui lòng kiểm tra file KV.",
            )

    def open_book(self, instance):
        if self.book_manager_instance is None:
            print("ERROR (LibraryScreen): BookManager instance is None. Cannot update library view.")
            show_error_popup(
                "Lỗi Khởi Tạo",
                "Không thể cập nhật giao diện thư viện vì BookManager không được khởi tạo.",
            )
            return
        book_name = instance.book_name
        if self.book_manager_instance.open_book(book_name):
            print(f"DEBUG (LibraryScreen - open_book): Sách '{book_name}' đã được mở thành công.")
        else:
            print(f"ERROR (LibraryScreen - open_book): Không thể mở sách '{book_name}'.")
            show_error_popup(
                "Lỗi Mở Sách",
                f"Không thể mở sách '{book_name}'.\nVui lòng kiểm tra lại.",
            )

    def pick_file(self):
        my_android_handler.pick_file()

    def pick_folder(self):
        my_android_handler.pick_folder()
