import os
import time

from textstoryreader.managers.historyreading_manager import HistoryReadingManager
from textstoryreader.models.book import Book
from textstoryreader.models.readingstate import ReadingState
from textstoryreader.services.android_handle import my_android_handler
from textstoryreader.services.parser_handle import ParserHandle
from textstoryreader.ui.utils import show_error_popup


class BookReader:
    def __init__(self, book: Book):
        self.book = book
        self.history_manager = HistoryReadingManager()
        self.index_word_start = 0
        self.book_data = None
        self.content_list = []
        self.chapter_list = []
        self.parser_handle = ParserHandle(self.book)

    def get_history_readingstate(self) -> ReadingState:
        return self.history_manager.get_history(self.book.book_name)

    def save_history_readingstate(self, index_word_start=None, last_chapter_order=None) -> None:
        print(f"Saving progress for: {self.book.book_name}")

        # Cập nhật thuộc tính nếu giá trị mới được truyền vào
        if last_chapter_order is not None:
            self.last_chapter_order = last_chapter_order
        if index_word_start is not None:
            self.index_word_start = index_word_start
        self.history_manager.save_history(
            book_name=self.book.book_name, last_chapter_order=self.last_chapter_order, index_word_start=self.index_word_start
        )

    def load_all_content_book(self):
        self.book.file_path = os.path.join(my_android_handler.book_folder_path, self.book.book_name)
        print(f"DEBUG <BookReader>  file path of book is {self.book.file_path}")
        if self.book_data:
            return self.book_data
        start_time = time.time()
        self.book_data = self.parser_handle.parse()
        print(f"DEBUG <BookReader> Loading book spend time :{time.time() - start_time}")
        # print(self.book_data)
        return self.book_data

    def get_content_chapter(self) -> dict:
        self.book_data = self.load_all_content_book()
        if not self.book_data:
            show_error_popup("lỗi file", "Book data is not exist, cannot retrieve content")
            return {"content": "", "last_chapter_order": 0, "index_word_start": 0}
        self.content_list = self.book_data[0]
        self.chapter_list = self.book_data[1]
        history = self.get_history_readingstate()
        self.last_chapter_order = history.last_chapter_order
        self.index_word_start = history.index_word_start

        if self.last_chapter_order < 0 or self.last_chapter_order >= len(self.content_list):
            self.save_history_readingstate()
            print("DEBUG (BookReader): Resetting last chapter order and position due to out of bounds.")
            show_error_popup("lỗi file", "chapter order is out of bounds")
            return {"content": "", "last_chapter_order": 0, "index_word_start": 0}

        return {
            "content": self.content_list[self.last_chapter_order],
            "last_chapter_order": self.last_chapter_order,
            "index_word_start": self.index_word_start,
        }

    def get_chapter_list(self) -> list:
        self.book_data = self.load_all_content_book()
        if not self.book_data:
            show_error_popup("lỗi file", "Book data is not exist, cannot retrieve content")
            return []
        return self.book_data[1]

    # def reload_book_data(self) -> dict:
    #     self.book_data = None
    #     self.book_data = self.load_all_content_book()
    #     print(f"len(self.book_data): {len(self.content_list)}")
    # return self.get_content_chapter()

    def next_chapter(self) -> dict:
        if self.last_chapter_order >= len(self.content_list) - 1:
            show_error_popup("lỗi file", "No next chapter available")
            # pass
            return {"content": "", "last_chapter_order": 0, "index_word_start": 0}
        self.last_chapter_order += 1
        self.index_word_start = 0
        self.save_history_readingstate()
        return self.get_content_chapter()

    def previous_chapter(self) -> dict:
        if self.last_chapter_order == 0:
            show_error_popup("lỗi file", "No previous chapter available")
            return {"content": "", "last_chapter_order": 0, "index_word_start": 0}
        self.last_chapter_order -= 1
        self.index_word_start = 0
        self.save_history_readingstate()
        return self.get_content_chapter()

    def jump_to_chapter(self, chapter_order: int) -> dict:
        self.last_chapter_order = chapter_order
        self.index_word_start = 0
        self.save_history_readingstate()
        return self.get_content_chapter()

    def jump_to_head(self) -> dict:
        self.last_chapter_order = 0
        self.index_word_start = 0
        self.save_history_readingstate()
        return self.get_content_chapter()
