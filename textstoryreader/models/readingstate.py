from dataclasses import dataclass


@dataclass
class ReadingState:
    book_name: str
    last_chapter_order: int = 0
    last_position_in_chapter: str
