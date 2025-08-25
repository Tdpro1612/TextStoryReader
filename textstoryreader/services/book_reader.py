import os

from textstoryreader.managers.historyreading_manager import HistoryReadingManager
from textstoryreader.models.book import Book
from textstoryreader.models.readingstate import ReadingState
from textstoryreader.services.android_handle import AndroidHandle
from textstoryreader.services.parser_handle import ParserHandle
from textstoryreader.ui.utils import show_error_popup


class BookReader:
    def __init__(self, book: Book):
        self.book = book
        self.history_manager = HistoryReadingManager()
        self.last_chapter_order = 0
        self.last_position_in_chapter = 1.0
        self.book_data = None
        self.android_handle = AndroidHandle()
        self.content_list = []
        self.chapter_list = []
        self.parser_handle = ParserHandle(self.book)

    def get_history_readingstate(self) -> ReadingState:
        return self.history_manager.get_history(self.book.book_name)

    def save_history_readingstate(self, last_position_in_chapter: float = 1.0) -> None:
        print(f"Saving progress for: {self.book.book_name}")
        self.history_manager.save_history(
            book_name=self.book.book_name,
            last_chapter_order=self.last_chapter_order,
            last_position_in_chapter=last_position_in_chapter,
        )

    def load_all_content_book(self):
        if self.android_handle.is_android:
            self.book.file_path = os.path.join(self.android_handle.get_android_paths(), self.book.book_name)
        else:
            self.book.file_path = f"textstoryreader/books/{self.book.book_name}"
        if self.book_data:
            return self.book_data
        self.book_data = self.parser_handle.parse()
        return self.book_data

    def get_content_chapter(self) -> dict:
        self.book_data = self.load_all_content_book()
        if not self.book_data:
            show_error_popup("lỗi file", "Book data is not exist, cannot retrieve content")
            return {"content": "", "last_chapter_order": 0, "last_position_in_chapter": 1.0}
        self.content_list = self.book_data[0]
        self.chapter_list = self.book_data[1]
        history = self.get_history_readingstate()
        self.last_chapter_order = history.last_chapter_order
        self.last_position_in_chapter = history.last_position_in_chapter

        if self.last_chapter_order < 0 or self.last_chapter_order >= len(self.content_list):
            self.last_chapter_order = 0
            self.last_position_in_chapter = 1.0
            self.save_history_readingstate()
            print("DEBUG (BookReader): Resetting last chapter order and position due to out of bounds.")
            show_error_popup("lỗi file", "chapter order is out of bounds")
            return {"content": "", "last_chapter_order": 0, "last_position_in_chapter": 1.0}

        # print(f"Đây là nội dung cần lấy {self.content_list[self.last_chapter_order]}")
        return {
            "content": self.content_list[self.last_chapter_order],
            "last_chapter_order": self.last_chapter_order,
            "last_position_in_chapter": self.last_position_in_chapter,
        }

    def get_chapter_list(self) -> list:
        self.book_data = self.load_all_content_book()
        if not self.book_data:
            show_error_popup("lỗi file", "Book data is not exist, cannot retrieve content")
            return []
        return self.book_data[1]

    def reload_book_data(self) -> dict:
        self.book_data = None
        self.book_data = self.load_all_content_book()
        print(f"len(self.book_data): {len(self.content_list)}")
        # return self.get_content_chapter()

    def next_chapter(self) -> dict:
        if self.last_chapter_order >= len(self.content_list) - 1:
            show_error_popup("lỗi file", "No next chapter available")
            # pass
            return {"content": "", "last_chapter_order": 0, "last_position_in_chapter": 1.0}
        self.last_chapter_order += 1
        self.last_position_in_chapter = 1.0
        self.save_history_readingstate()
        return {"content": "", "last_chapter_order": self.last_chapter_order, "last_position_in_chapter": 1.0}

    def previous_chapter(self) -> dict:
        if self.last_chapter_order == 0:
            show_error_popup("lỗi file", "No previous chapter available")
            return {"content": "", "last_chapter_order": 0, "last_position_in_chapter": 1.0}
        self.last_chapter_order -= 1
        self.last_position_in_chapter = 1.0
        self.save_history_readingstate()
        return {"content": "", "last_chapter_order": self.last_chapter_order, "last_position_in_chapter": 1.0}

    def jump_to_chapter(self, chapter_order: int) -> dict:
        self.last_chapter_order = chapter_order
        self.last_position_in_chapter = 1.0
        self.save_history_readingstate()
        # return self.get_content_chapter()

    def jump_to_head(self, chapter_order: int = 0) -> dict:
        self.last_chapter_order = chapter_order
        self.last_position_in_chapter = 1.0
        self.save_history_readingstate()
        # return self.get_content_chapter()
