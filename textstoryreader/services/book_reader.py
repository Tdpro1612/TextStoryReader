import os

from textstoryreader.managers.historyreading_manager import HistoryReadingManager
from textstoryreader.models.book import Book
from textstoryreader.models.readingstate import ReadingState
from textstoryreader.services.android_handle import AndroidHandle


class BookReader:
    def __init__(self, book: Book, history_manager: HistoryReadingManager):
        self.book = book
        self.history_manager = history_manager
        self.last_chapter_order = 0
        self.last_position_in_chapter = 0.0
        self.book_data = None
        self.android_handle = AndroidHandle()

    def get_history_readingstate(self) -> ReadingState:
        return self.history_manager.get_history(self.book.book_name)

    def save_history_readingstate(self) -> None:
        print(f"Saving progress for: {self.book.book_name}")
        self.history_manager.save_history(
            book_name=self.book.book_name,
            last_chapter_order=self.last_chapter_order,
            last_position_in_chapter=self.last_position_in_chapter,
        )

    def load_all_content_book(self) -> list:
        if self.android_handle.is_android():
            self.book.file_path = os.path.join(self.android_handle.get_android_paths(), self.book.book_name)
        else:
            self.book.file_path = f"textstoryreader/books/{self.book.book_name}"
        if self.book_data:
            return self.book_data
        if self.book.file_extension == ".txt":
            self.book_data = self.load_txt_book(self.book.file_path)
        elif self.book.file_extension == ".html":
            self.book_data = self.load_html_book(self.book.file_path)
        else:
            raise ValueError("Unsupported book format")
        return self.book_data

    def get_content_chapter(self) -> dict:
        self.book_data = self.load_all_content_book()
        if not self.book_data:
            raise ValueError("Book data is not exist, cannot retrieve content")

        history = self.get_history_readingstate()
        self.last_chapter_order = history.last_chapter_order
        self.last_position_in_chapter = history.last_position_in_chapter

        if self.last_chapter_order < 0 or self.last_chapter_order >= len(self.book_data):
            self.last_chapter_order = 0
            self.last_position_in_chapter = 0.0
            self.save_history_readingstate()
            print("DEBUG (BookReader): Resetting last chapter order and position due to out of bounds.")
            raise IndexError("chapter order is out of bounds")

        return {
            "content": self.book_data[self.last_chapter_order],
            "last_position_in_chapter": self.last_position_in_chapter,
        }

    def reload_book_data(self) -> dict:
        self.book_data = None
        self.book_data = self.load_all_content_book()
        return self.get_content_chapter()

    def next_chapter(self) -> dict:
        if self.last_chapter_order >= len(self.book_data) - 1:
            raise IndexError("No next chapter available")
        self.last_chapter_order += 1
        self.last_position_in_chapter = 0.0
        self.save_history_readingstate()
        return self.get_content_chapter()

    def previous_chapter(self) -> dict:
        if self.last_chapter_order == 0:
            raise IndexError("No previous chapter available")
        self.last_chapter_order -= 1
        self.last_position_in_chapter = 0.0
        self.save_history_readingstate()
        return self.get_content_chapter()

    def jump_to_chapter(self, chapter_order: int) -> dict:
        self.last_chapter_order = chapter_order
        self.last_position_in_chapter = 0.0
        self.save_history_readingstate()
        return self.get_content_chapter()

    def jump_to_head(self, chapter_order: int = 0) -> dict:
        self.last_chapter_order = chapter_order
        self.last_position_in_chapter = 0.0
        self.save_history_readingstate()
        return self.get_content_chapter()
