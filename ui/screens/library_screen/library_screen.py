# library_screen.py

import os

from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

# KHÔNG KHỞI TẠO book_manager Ở ĐÂY NỮA
# from managers.book_manager import BookManager
# book_manager = BookManager() # <--- Bỏ dòng này


class LibraryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print(f"DEBUG (LibraryScreen): __init__ method called! Instance: {self}")
        # Không truy cập self.ids ở đây, vì nó chưa chắc đã được ánh xạ.
        # Logic này sẽ được xử lý trong on_enter hoặc update_library_view.

    def on_enter(self, *args):
        # Khi màn hình được hiển thị, cập nhật giao diện thư viện
        print("DEBUG (LibraryScreen): on_enter method called. Updating library view.")
        self.update_library_view()

    def update_library_view(self):
        # Đảm bảo grid_layout_stories đã được ánh xạ từ file .kv
        if "grid_layout_stories" in self.ids:
            self.grid_layout_stories = self.ids.grid_layout_stories
            print(
                "DEBUG (LibraryScreen): 'grid_layout_stories' found in self.ids (in update_library_view)."
            )

            # Truy cập book_manager thông qua App
            app = App.get_running_app()
            if hasattr(app, "managers") and hasattr(app.managers, "book_manager"):
                book_manager_instance = app.managers.book_manager
                print(
                    "DEBUG (LibraryScreen): BookManager instance retrieved from App.managers."
                )
            else:
                print(
                    "ERROR (LibraryScreen): BookManager not found in App.managers. Make sure it's initialized in your App class."
                )
                self.show_error_popup(
                    "Lỗi Khởi Tạo",
                    "Không thể tìm thấy BookManager.\nVui lòng kiểm tra cấu hình ứng dụng.",
                )
                return

            book_list = book_manager_instance.get_book_list()
            self.grid_layout_stories.clear_widgets()

            if book_list:
                print(
                    "DEBUG (LibraryScreen - display_library): book_list có sách, bắt đầu thêm nút."
                )
                for book_name, filename in book_list:
                    book_button = Button(
                        text=book_name, size_hint_y=None, height=dp(80)
                    )
                    book_button.book_filename = filename
                    book_button.bind(on_press=self.open_book)
                    self.grid_layout_stories.add_widget(book_button)
            else:
                print(
                    "DEBUG (LibraryScreen - display_library): book_list trống, hiển thị thông báo không có sách."
                )
                no_books_label = Label(
                    text="Không có sách nào trong thư viện.",
                    halign="center",
                    valign="middle",
                    text_size=self.grid_layout_stories.size,  # Đảm bảo text_size phù hợp với kích thước layout chứa nó
                )
                self.grid_layout_stories.add_widget(no_books_label)
        else:
            print(
                "ERROR (LibraryScreen): 'grid_layout_stories' not found in self.ids (in update_library_view). Check KV file."
            )
            self.show_error_popup(
                "Lỗi Giao Diện",
                "Không thể tìm thấy thành phần giao diện 'grid_layout_stories'.\nVui lòng kiểm tra file KV.",
            )

    def open_book(self, instance):
        book_filename = instance.book_filename

        app = App.get_running_app()
        if hasattr(app, "managers") and hasattr(app.managers, "book_manager"):
            book_manager_instance = app.managers.book_manager
        else:
            print(
                "ERROR (LibraryScreen): BookManager not found when trying to open book."
            )
            self.show_error_popup(
                "Lỗi Hệ Thống", "Không thể truy cập BookManager để mở sách."
            )
            return

        # Sử dụng BookManager để đọc nội dung sách
        book_data, chapter_list, error_type = book_manager_instance.read_book_content(
            book_filename
        )
        book_name = (
            os.path.splitext(os.path.basename(book_filename))[0]
            .replace("_", " ")
            .title()
        )  # Lấy tên file base

        # Xử lý các loại lỗi từ BookManager
        if error_type == "file_not_found":
            print(f"DEBUG (open_book): File sách không tồn tại: {book_filename}")
            self.show_error_popup(
                "Lỗi File",
                f"File sách '{os.path.basename(book_filename)}' không tìm thấy.\nVui lòng kiểm tra lại.",
            )
            return
        elif error_type == "unsupported_format":
            print(
                f"DEBUG (open_book): Định dạng file không được hỗ trợ: {book_filename}"
            )
            self.show_error_popup(
                "Định dạng File Không Hỗ Trợ",
                f"Ứng dụng không hỗ trợ định dạng file '{os.path.basename(book_filename)}'.\nVui lòng chọn file .txt hoặc .html.",
            )
            return
        elif error_type == "read_error":
            print(
                f"DEBUG (open_book): Không thể đọc nội dung sách: {book_name} ({book_filename})"
            )
            self.show_error_popup(
                "Lỗi Đọc Sách",
                f"Ứng dụng gặp vấn đề khi đọc file sách '{os.path.basename(book_filename)}'.\nVui lòng kiểm tra lại file hoặc thử sách khác.",
            )
            return

        # Nếu không có lỗi và có dữ liệu sách
        if book_data:
            # reader_screen và chapter_screen phải được thêm vào ScreenManager trong App class
            # và có tên 'reader_screen' và 'chapter_screen' tương ứng.
            if app.root.has_screen("reader_screen") and app.root.has_screen(
                "chapter_screen"
            ):
                reader_screen = app.root.get_screen("reader_screen")
                chapter_screen = app.root.get_screen("chapter_screen")

                # Tải nội dung vào ReaderScreen
                reader_screen.load_book_content(
                    book_filename,
                    book_name,
                    book_data,
                    history_chapter_index=0,
                    history_chapter_page=0,
                )

                # Tải danh sách chương vào ChapterScreen
                chapter_screen.load_chapters(chapter_list)

                # Chuyển sang ReaderScreen
                self.manager.current = "reader_screen"

                print(
                    f"DEBUG (open_book): Sách '{book_name}' đã được tải và chuyển sang màn hình đọc."
                )
            else:
                print(
                    "ERROR (open_book): ReaderScreen or ChapterScreen not found in ScreenManager."
                )
                self.show_error_popup(
                    "Lỗi Điều Hướng",
                    "Không thể tìm thấy màn hình đọc hoặc màn hình chương.\nVui lòng kiểm tra cấu hình ScreenManager.",
                )
        else:
            print(
                f"DEBUG (open_book): Không có dữ liệu sách sau khi đọc: {book_name} ({book_filename})"
            )
            self.show_error_popup(
                "Lỗi Đọc Sách",
                f"Không có nội dung nào được tìm thấy trong file sách '{os.path.basename(book_filename)}'.",
            )

    def show_error_popup(self, title, message):
        """
        Hiển thị một cửa sổ Popup thông báo lỗi cho người dùng.
        """
        content = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        content.add_widget(
            Label(
                text=message,
                halign="center",
                valign="middle",
                text_size=(dp(250), None),
            )
        )

        close_button = Button(text="Đóng", size_hint=(1, None), height=dp(40))
        content.add_widget(close_button)

        popup = Popup(
            title=title,
            content=content,
            size_hint=(None, None),
            size=(dp(300), dp(200)),
            auto_dismiss=False,
        )

        close_button.bind(on_release=popup.dismiss)
        popup.open()
        print(f"DEBUG (show_error_popup): Popup lỗi đã hiển thị: {title} - {message}")
