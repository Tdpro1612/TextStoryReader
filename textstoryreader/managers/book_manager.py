import os
from typing import List

from kivy.app import App

from textstoryreader.constants import SUPPORTED_EXTENSIONS
from textstoryreader.models.book import Book
from textstoryreader.services.android_handle import my_android_handler


class BookManager:
    def __init__(self):
        self.book_folder_path = my_android_handler.book_folder_path
        self._books = []

    def add_book(self):
        pass

    def delete_book(self):
        """
        Input: Book object hoặc bookId (ID duy nhất của sách).

        Output: boolean (thành công/thất bại).

        Lý do: Cung cấp một cách rõ ràng để loại bỏ sách khỏi thư viện.
        """
        pass

    def get_book_list(self) -> List[Book]:
        self._books.clear()
        files_in_folder = os.listdir(self.book_folder_path)
        for book_name in files_in_folder:
            book_file_path = os.path.join(self.book_folder_path, book_name)

            # Bỏ qua nếu là thư mục con
            if os.path.isdir(book_file_path):
                print(f"DEBUG (BookManager): Bỏ qua thư mục con: {book_name}")
                continue

            # Kiểm tra định dạng file txt or html
            file_extension = os.path.splitext(book_name)[1].lower()
            if file_extension in SUPPORTED_EXTENSIONS:
                try:
                    book_title = os.path.splitext(book_name)[0].replace("_", " ").title()
                    # Tạo đối tượng Book
                    new_book = Book(book_name, book_title, book_file_path, file_extension)
                    self._books.append(new_book)
                except Exception as e:
                    print(f"ERROR (BookManager): Không thể phân tích file '{book_name}': {e}")
        return self._books

    def open_book(self, book_name) -> bool:
        if not book_name:
            print("ERROR (BookManager): book_name is empty. Cannot open book.")
            return False
        for book in self._books:
            if book.book_name == book_name:
                app = App.get_running_app()
                if app.root.has_screen("reader_screen") and app.root.has_screen("chapter_screen"):
                    reader_screen = app.root.get_screen("reader_screen")
                    reader_screen.set_book(book)
                    reader_screen.update_reader_view()
                    app.root.current = "reader_screen"
                    chapter_screen = app.root.get_screen("chapter_screen")
                    chapter_screen.set_book(book)
                    chapter_screen.update_chapterlist_view()
                return True
        return False
