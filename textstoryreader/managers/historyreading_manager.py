from typing import Dict

from textstoryreader.models.readingstate import ReadingState


class HistoryReadingManager:
    def __init__(self):
        self.history = {}

    def save_history(self, book_name: str, last_chapter_order: int, last_position_in_chapter: float):
        self.history[book_name] = ReadingState(
            book_name=book_name, last_chapter_order=last_chapter_order, last_position_in_chapter=last_position_in_chapter
        )
        print(f"DEBUG (ReadingHistoryManager): Saved history for {book_name}")

    def get_all_history(self) -> Dict[ReadingState]:
        return self.history

    def get_history(self, book_name: str) -> ReadingState:
        return self.history.get(book_name, ReadingState(book_name=book_name))

    def clear_history(self) -> None:
        self.history.clear()
